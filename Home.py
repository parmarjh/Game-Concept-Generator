import os
import json

import sqlite3
import streamlit as st

from classes.game import GameProjectManager, ProjectType, ArtStyle, ConceptType, GameConcept, GameProject

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(layout="wide", page_title="Game Concept Generator", page_icon="🎮")

with open("README.md", "r", encoding="utf-8") as file:
    readme_content = file.read()

def initialize_database():
    conn = sqlite3.connect("game_project.db")
    c = conn.cursor()

    try:
        # Crear tablas
        c.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY, name TEXT, project_type TEXT, art_style TEXT,
                target_audience TEXT, core_mechanics TEXT, high_concept TEXT,
                unique_selling_points TEXT, target_platform TEXT, team_size TEXT,
                budget_range TEXT, created_at TEXT, project_status TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id TEXT PRIMARY KEY, project_id TEXT, type TEXT, name TEXT, description TEXT,
                generated_video TEXT, reference_links TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        conn.commit()
    except Exception as e:
        st.error(f"Error al crear tablas en la base de datos: {e}")

    # Cargar proyectos existentes en session_state
    st.session_state['projects'] = []
    c.execute('SELECT * FROM projects')
    projects_data = c.fetchall()
    print(projects_data)
    for project_data in projects_data:
        project = GameProject(
            id=project_data[0],
            name=project_data[1],
            project_type=ProjectType(project_data[2]),
            art_style=ArtStyle(project_data[3]),
            target_audience=project_data[4],
            core_mechanics=project_data[5].split('\n'),
            high_concept=project_data[6],
            unique_selling_points=project_data[7].split('\n'),
            target_platform=project_data[8].split(','),
            team_size=project_data[9],
            budget_range=project_data[10],
            created_at=project_data[11],
            project_status=project_data[12]
        )
        st.session_state['projects'].append(project)

    conn.close()


def load_concepts_from_db(project_id):
    conn = sqlite3.connect("game_project.db")
    c = conn.cursor()
    c.execute('SELECT * FROM concepts WHERE project_id = ?', (project_id,))
    concepts_data = c.fetchall()
    concepts = []
    for concept_data in concepts_data:
        concepts.append(GameConcept(
            type=ConceptType(concept_data[2]),
            name=concept_data[3],
            description=concept_data[4],
            generated_video=concept_data[5],
            references=concept_data[6].split("\n")
        ))
    conn.close()
    return concepts

try:
    initialize_database()
except Exception as e:
    st.error(f"Error initializing database: {e}")

# Initialize session state
if 'ARIA_API_KEY' not in st.session_state:
    st.session_state['ARIA_API_KEY'] = os.getenv('RHYMESAI_API_KEY')

if 'project_manager' not in st.session_state:
    st.session_state.project_manager = GameProjectManager()

# Streamlit App Layout
def main():
    
    # Custom CSS
    # st.markdown("""
    #     <style>
    #     .stTabs [data-baseweb="tab-list"] {
    #         gap: 2px;
    #     }
    #     .stTabs [data-baseweb="tab"] {
    #         padding: 10px 20px;
    #         background-color: #262730;
    #     }
    #     .stTabs [aria-selected="true"] {
    #         background-color: #0E1117;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)
    
    with st.sidebar:
        ARIA_API_KEY = st.text_input("Ingresa tu Rhymes AI API Key", type="password", value=st.session_state['ARIA_API_KEY'])
        if ARIA_API_KEY:
            st.session_state['ARIA_API_KEY'] = ARIA_API_KEY
            st.success("API Key ingresada correctamente.")

    # Main Title with Emoji
    # st.title("🎮 Game Concept Generator & Prototyping Tool")

    # Mostrar el contenido en Streamlit usando Markdown
    st.markdown(readme_content, unsafe_allow_html=True)

if __name__ == "__main__":
    main()