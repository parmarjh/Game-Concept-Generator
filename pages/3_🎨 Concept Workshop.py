import os
from typing import List
import time
from datetime import datetime 
import sqlite3

import streamlit as st

from classes.game import GameProjectManager, ProjectType, ArtStyle, ConceptType, GameConcept, GameProject
from classes.Aria import Aria
from classes.Allegro import Allegro




# Initialize session state
if 'ARIA_API_KEY' not in st.session_state:
    st.session_state['ARIA_API_KEY'] = os.getenv('RHYMESAI_API_KEY')

def load_concepts_from_db(project_id):
    conn = sqlite3.connect("game_project.db")
    c = conn.cursor()
    c.execute('SELECT * FROM concepts WHERE project_id = ?', (project_id,))
    concepts_data = c.fetchall()
    concepts = []
    for concept_data in concepts_data:
        # print(concept_data)
        concepts.append(GameConcept(
            type=ConceptType(concept_data[2]),
            name=concept_data[3],
            description=concept_data[4],
            references=concept_data[5].split("\n"),
            generated_video=concept_data[6]
        ))
    conn.close()
    return concepts

def generate_concept(
        project: GameProject,
        concept_type: ConceptType, 
        name: str, 
        description: str, 
        related_concepts: List[str], 
        uploaded_files) -> GameConcept:
    aria = Aria(api_key=st.session_state['ARIA_API_KEY'])
    allegro = Allegro(api_key=st.session_state['ARIA_API_KEY'])

    # Generate concept prompt
    prompt = f"""
Generate a {concept_type.value} concept for a {project.project_type.value} game with the following details:
* Name: ´´´{name}´´´
* Description: ´´´{description}´´´
"""
    if related_concepts:
        prompt += f"\nRelated Concepts: {', '.join(related_concepts)}"

    # Use Aria to generate the concept
    messages = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # print(uploaded_file.getvalue())
            base64_string = aria.base64_url(uploaded_file)   #aria.image_to_base64(uploaded_file)
            messages.append(
                {"role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_string}"}},
                        {"type": "text", "text": "<image>\nUse this image for the concept."}
                    ]
                }
            )

    messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})

    response = aria.chat(messages)
    concept_description = response.choices[0].message.content
    # print(f"Concept Description: {concept_description}")

    # Generate video prompt
#     video_prompt = f"""
# Generate a high-fidelity video prompt visualizing a {concept_type.value} concept for a {project.project_type.value} game with a strong sense of {project.art_style.value} art style. Focus on bringing to life the game's theme and setting with dynamic elements that immerse the viewer in its unique world. Include the following details:

# 1. **Name**: {name}
# 2. **Description**: {description}
# 3. **Core Themes and Related Concepts**: {', '.join(related_concepts)}
# 4. **Visual and Environmental Details**: Highlight key scenes and interactions. Include elements like lighting, textures, and environmental aspects that reflect {project.art_style.value}.
# 5. **Character and Object Design**: Describe the appearance and style of characters or primary objects in the scene, capturing their traits, outfits, and any defining animations.
# 6. **Mood and Tone**: Emphasize emotions or atmospheres (e.g., mysterious, adventurous) that align with the {concept_type.value} concept.
# """
    
    video_prompt = f"""
* Concept Value: ´´´{concept_type.value}´´´
* Concept description: ´´´{concept_description}´´´
* Genre game: ´´´{project.project_type.value}´´´
* Art style: ´´´{project.art_style.value}´´´
"""
    if related_concepts:
        video_prompt += f"* Related Concepts: ´´´{', '.join(related_concepts) }´´´"
    
    # 7. **Interactive/Game Elements**: (Optional) Show elements of gameplay, key moves, or interactions to give a sense of playability.

    # response = aria.chat([
    #     {"role": "user", "content": [{"type": "text", "text": video_prompt}]}
    # ])
    
    # video_prompt_description = response.choices[0].message.content
    # print(f"Video Description: {video_prompt_description}")

    # Use Allegro to generate the video
    video_data = {
        "refined_prompt": video_prompt,  #_description,
        "num_step": 100,
        "cfg_scale": 7.5,
        "user_prompt": video_prompt,
        "rand_seed": 12345
    }

    video_response = allegro.generate_video(video_data)
    # print(f"Video Response: {video_response}")
    video_id = video_response.get("data")
    max_attempts = 10

    for attempt in range(max_attempts):
        # Call the video status query
        status_response = allegro.query_video_status(video_id)

        # Check if the response is empty
        if status_response['data'] == "":
            print(f"Attempt {attempt + 1}: Status response is empty. Retrying...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
        else:
            print(f"Attempt {attempt + 1}: Status response received: {status_response}")
            break  # Exit the loop if a valid response is received
    else:
        print("Maximum attempts reached. No valid response received.")

    # status_response = allegro.query_video_status(video_id)

    video_url = status_response["data"]

    # Create the GameConcept object
    concept = GameConcept(
        type=ConceptType(concept_type),
        name=name,
        description=concept_description,
        references=[concept_description,video_prompt],
        generated_video=video_url,
        related_concepts=related_concepts
    )

    return concept

with st.sidebar:
    ARIA_API_KEY = st.text_input("Ingresa tu Rhymes AI API Key", type="password", value=st.session_state['ARIA_API_KEY'])
    if ARIA_API_KEY:
        st.session_state['ARIA_API_KEY'] = ARIA_API_KEY
        st.success("API Key ingresada correctamente.")

    if 'selected_project' in st.session_state:
        if st.session_state['selected_project'] is not [] and st.session_state['selected_project'] is not None:
            st.header(f"📝 {st.session_state['selected_project'].name} 📝")
            # st.info(f"Status: {st.session_state['selected_project'].project_status}")
            st.caption(f"Created: {datetime.strptime(st.session_state['selected_project'].created_at ,'%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d')}")


if 'selected_project' in st.session_state and st.session_state['selected_project'] is not [] and st.session_state['selected_project'] is not None:
    st.subheader("✨ Create New Concept")

    st.session_state.concepts = load_concepts_from_db(st.session_state['selected_project'].id)
    # print(f"Conceptos : {st.session_state.concepts}")

    cols = st.columns([1, 2])
    with cols[0]:
        concept_type = st.selectbox("Concept Type", options=[t.value for t in ConceptType])
        name = st.text_input("Concept Name")
        description = st.text_area("Description")
        related = st.multiselect("Related Concepts", 
            options=[c.name for c in st.session_state.concepts])
        
        uploaded_files = st.file_uploader(
            "Reference Images", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        
        if st.button("🔮 Generate Concept"):
            with st.spinner("Generating concept 🤖... Approximate time: 2 minutes (Don't refresh)"):
                concept = generate_concept(
                    st.session_state['selected_project'],
                    ConceptType(concept_type),
                    name,
                    description,
                    related,
                    uploaded_files
                )

                st.session_state.project_manager.add_concept(st.session_state['selected_project'].id, concept)
                # st.session_state['selected_project'].concepts[concept.id] = concept

                st.success("Concept generated successfully! ✨")

    with cols[1]:
        st.subheader("📚 Concept Gallery")
        if st.session_state.concepts:
            for concept in st.session_state.concepts:
                with st.expander(f"{concept.type.value.capitalize()}: {concept.name}"):
                    st.write(concept.description)
                    # print(f"Video URL: {concept.generated_video}")    
                    st.video(concept.generated_video)
                    
                    # cols = st.columns(2)
                    # with cols[0]:
                    #     st.write("**Related Concepts:**")
                    #     for rel in concept.related_concepts:
                    #         st.write(f"- {rel}")
                    
                    # with cols[1]:
                    #     if concept.feedback_notes:
                    #         st.write("**Feedback:**")
                    #         for note in concept.feedback_notes:
                    #             st.write(f"- {note}")