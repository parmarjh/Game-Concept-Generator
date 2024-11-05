import os
from datetime import datetime 
import streamlit as st

from classes.game import GameProjectManager, ProjectType, ArtStyle, ConceptType, GameConcept

# Initialize session state
if 'ARIA_API_KEY' not in st.session_state:
    st.session_state['ARIA_API_KEY'] = os.getenv('RHYMESAI_API_KEY')

with st.sidebar:
    ARIA_API_KEY = st.text_input("Ingresa tu Rhymes AI API Key", type="password", value=st.session_state['ARIA_API_KEY'])
    if ARIA_API_KEY:
        st.session_state['ARIA_API_KEY'] = ARIA_API_KEY
        st.success("API Key ingresada correctamente.")

st.header("📂 Project Management")

# Project Creation
with st.expander("➕ Create New Project"):
    with st.form("new_project"):
        cols = st.columns(2)
        with cols[0]:
            project_name = st.text_input("Project Name")
            project_type = st.selectbox("Project Type", options=[t.value for t in ProjectType])
            art_style = st.selectbox("Art Style", options=[s.value for s in ArtStyle])
        
        with cols[1]:
            target_audience = st.text_input("Target Audience")
            target_platform = st.multiselect("Target Platform", 
                ["PC", "Mobile", "Console", "VR", "Web", "Cross-platform"])
            team_size = st.selectbox("Team Size", 
                ["Solo", "Small (2-5)", "Medium (6-15)", "Large (16+)"])
        
        st.subheader("Core Game Elements")
        high_concept = st.text_area("High Concept (One sentence pitch)")
        mechanics = st.text_area("Core Mechanics (one per line)")
        usp = st.text_area("Unique Selling Points (one per line)")
        
        cols = st.columns(2)
        with cols[0]:
            project_status = st.selectbox("Project Status", 
                ["Pre-production", "Prototyping", "Production", "Polish"])
        with cols[1]:
            budget_range = st.selectbox("Budget Range",
                ["< $10K", "$10K - $50K", "$50K - $200K", "$200K+"])
        
        submitted = st.form_submit_button("🚀 Create Project")
        if submitted:
            try:
                project = st.session_state.project_manager.create_project(
                    name=project_name,
                    project_type=ProjectType(project_type),
                    art_style=ArtStyle(art_style),
                    target_audience=target_audience,
                    core_mechanics=mechanics.split('\n'),
                    high_concept=high_concept,
                    unique_selling_points=usp.split('\n'),
                    target_platform=target_platform,
                    team_size=team_size,
                    project_status=project_status,
                    budget_range=budget_range
                )
                print(f"Project created: {project}")
            except Exception as e:
                print(f"Error creating project: {e}")
                st.error(f"Error creating project: {e}")
            st.success(f"Project '{project_name}' created successfully! 🎉")

# Project Selection
if 'projects' in st.session_state:
    projects = list(st.session_state.project_manager.projects.values())
    projects = sorted(st.session_state['projects'], key=lambda x: x.name)
    st.divider()
    st.session_state['selected_project'] = st.selectbox(
        "📌 Select Active Project", 
        options=projects, 
        format_func=lambda x: x.name
    )
    
    if st.session_state['selected_project']:
        st.header(f"📝 {st.session_state['selected_project'].name} 📝")
        st.info(f"Status: {st.session_state['selected_project'].project_status}")
        st.caption(f"Created: {datetime.strptime(st.session_state['selected_project'].created_at ,'%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d')}")
    
        cols = st.columns([2, 1])
        with cols[0]:
            st.subheader("Project Summary")
            st.write(f"**High Concept:** {st.session_state['selected_project'].high_concept}")
            
            st.write("**Unique Selling Points:**")
            for i, usp in enumerate(st.session_state['selected_project'].unique_selling_points, 1):
                if usp.strip():
                    st.write(f"{i}. {usp}")
            
            st.write("**Core Mechanics:**")
            for mech in st.session_state['selected_project'].core_mechanics:
                if mech.strip():
                    st.write(f"- {mech}")

        with cols[1]:
            # Project Metadata Card
            st.markdown("### 📋 Project Details")
            meta_data = {
                "Genre": st.session_state['selected_project'].project_type.value,
                "Art Style": st.session_state['selected_project'].art_style.value,
                "Target Audience": st.session_state['selected_project'].target_audience,
                "Team Size": st.session_state['selected_project'].team_size,
                "Budget": st.session_state['selected_project'].budget_range,
                "Platforms": ", ".join(st.session_state['selected_project'].target_platform)
            }
            for key, value in meta_data.items():
                st.write(f"**{key}:** {value}")
