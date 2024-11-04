from datetime import datetime 
import streamlit as st

from classes.game import GameProjectManager, ProjectType, ArtStyle, ConceptType, GameConcept

with st.sidebar:
    ARIA_API_KEY = st.text_input("Ingresa tu Rhymes AI API Key", type="password", value=st.session_state['ARIA_API_KEY'])
    if ARIA_API_KEY:
        st.session_state['ARIA_API_KEY'] = ARIA_API_KEY
        st.success("API Key ingresada correctamente.")

    if st.session_state['selected_project']:
        print(st.session_state['selected_project'])
        st.header(f"📝 {st.session_state['selected_project'].name} 📝")
        # st.info(f"Status: {st.session_state['selected_project'].project_status}")
        st.caption(f"Created: {datetime.strptime(st.session_state['selected_project'].created_at ,'%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d')}")


st.subheader("✨ Create New Concept")

cols = st.columns([1, 2])
with cols[0]:
    concept_type = st.selectbox("Concept Type", options=[t.value for t in ConceptType])
    name = st.text_input("Concept Name")
    description = st.text_area("Description")
    related = st.multiselect("Related Concepts", 
        options=[c.name for c in st.session_state['selected_project'].concepts.values()])
    
    uploaded_files = st.file_uploader(
        "Reference Images", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )
    
    if st.button("🔮 Generate Concept"):
        with st.spinner("Generating concept..."):
            # Create concept logic here
            st.success("Concept generated successfully! ✨")

with cols[1]:
    st.subheader("📚 Concept Gallery")
    if st.session_state['selected_project'].concepts:
        for concept in st.session_state['selected_project'].concepts.values():
            with st.expander(f"{concept.type.value.capitalize()}: {concept.name}"):
                st.write(concept.description)
                
                cols = st.columns(2)
                with cols[0]:
                    st.write("**Related Concepts:**")
                    for rel in concept.related_concepts:
                        st.write(f"- {rel}")
                
                with cols[1]:
                    if concept.feedback_notes:
                        st.write("**Feedback:**")
                        for note in concept.feedback_notes:
                            st.write(f"- {note}")