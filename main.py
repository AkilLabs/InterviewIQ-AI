import streamlit as st
from streamlit_option_menu import option_menu
import pdf1, url_data, ag, hr_ques, ai_interview

def set_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    body, .stApp {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        font-family: 'Inter', sans-serif;
        animation: backgroundAnimation 10s infinite alternate;
        margin: 0;
        padding: 0;
    }

    @keyframes backgroundAnimation {
        0% {
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        }
        50% {
            background: linear-gradient(135deg, #0f3460, #16213e, #1a1a2e);
        }
        100% {
            background: linear-gradient(135deg, #16213e, #1a1a2e, #0f3460);
        }
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(31, 41, 55, 0.5);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Menu Container Styling */
    [data-testid="stSidebarNav"] {
        background: transparent;
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 10px;
        margin: 10px;
    }

    /* Option Menu Custom Styling */
    .nav-link {
        background: rgba(31, 41, 55, 0.3);
        border-radius: 10px;
        margin: 8px 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .nav-link:hover {
        background: rgba(31, 41, 55, 0.7) !important;
        transform: translateX(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .nav-link-selected {
        background: linear-gradient(90deg, #3B82F6, #1D4ED8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Main Content Area Styling */
    .stButton>button {
        transition: all 0.3s ease;
        transform: perspective(1px) translateZ(0);
        backface-visibility: hidden;
        background: rgba(31, 41, 55, 0.5) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        background-color: rgba(31, 41, 55, 0.7) !important;
    }
    .stButton>button:active {
        transform: scale(0.95);
    }

    .file-uploader {
        background: rgba(31, 41, 55, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
        color: white;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .file-uploader:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .card-container {
        background-color: rgba(31, 41, 55, 0.7);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .card-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }

    h1, h2, h3 {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Custom Menu Title Styling */
    .menu-title {
        color: white;
        font-size: 24px;
        font-weight: 600;
        text-align: center;
        padding: 20px 0;
        background: rgba(31, 41, 55, 0.3);
        border-radius: 15px;
        margin: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

class MultiApp:
    def __init__(self):
        self.apps = []
        
    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })
        
    def run(self):
        # Set page config
        st.set_page_config(
            page_title="InterviewIQ AI",
            page_icon="🤖",
            layout="wide"
        )
        
        # Apply custom CSS
        set_custom_css()
        
        # Create sidebar navigation
        with st.sidebar:
            st.markdown('<div class="menu-title">InterviewIQ AI</div>', unsafe_allow_html=True)
            
            selected = option_menu(
                menu_title=None,
                options=['PDF Analysis', 'URL Analysis', 'AI Trainer', 'HR Questions', 'AI Interviewer'],
                icons=['file-pdf', 'link', 'robot', 'person-workspace', 'chat-dots'],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "8px 0",
                        "padding": "15px",
                        "--hover-color": "rgba(31, 41, 55, 0.7)",
                    },
                    "nav-link-selected": {"background-color": "transparent"},
                }
            )

        # Route to appropriate page
        if selected == 'PDF Analysis':
            pdf1.app()
        elif selected == 'URL Analysis':
            url_data.app()
        elif selected == 'AI Trainer':
            ag.app()
        elif selected == 'HR Questions':
            hr_ques.app()
        elif selected == 'AI Interviewer':
            ai_interview.app()

# Initialize and run the app
if __name__ == "__main__":
    app = MultiApp()
    app.run()