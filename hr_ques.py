import streamlit as st
import os
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from crewai import Crew, Process, Agent, Task

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
        transform: translateY(-10px);
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
        transform: translateY(-10px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }

    h1, h2, h3 {
        color: white !important;
        font-weight: 600 !important;
    }

    .stTextArea>div>div {
        background-color: rgba(31, 41, 55, 0.5) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    .output-container {
        background: rgba(31, 41, 55, 0.5);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }

    .progress-container {
        background: rgba(31, 41, 55, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def create_file_uploader_section():
    st.markdown('<div class="card-container file-uploader">', unsafe_allow_html=True)
    st.subheader("📄 Upload Your Document")
    uploaded_file = st.file_uploader(
        "Upload an image or a PDF file", 
        type=["jpg", "jpeg", "png", "pdf"],
        help="Supported formats: JPG, JPEG, PNG, PDF"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return uploaded_file

def display_analysis_results(result):
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("🤖 AI Analysis Results")
    st.markdown('<div class="output-container">', unsafe_allow_html=True)
    st.write(result)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def process_document(uploaded_file):
    if uploaded_file:
        with st.spinner('Processing your document...'):
            # File type determination
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            # Save the file temporarily
            temp_file_path = f"temp_file{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Upload to generative model
            uploaded_file_path = genai.upload_file(temp_file_path)
            
            # Generate content
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = "Extract and analyze the content from this document. Present key points in a structured format:"
            
            response = model.generate_content([
                uploaded_file_path,
                "\n\n",
                prompt
            ])
            
            return response.text
    return None

def generate_hr_questions(content):
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("📝 Generated Interview Questions")
    
    with st.spinner('Generating interview questions...'):
        llm = GoogleGenerativeAI(
            model="gemini-1.5-flash",
            verbose=True,
            temperature=0.5,
            google_api_key='AIzaSyBqlzrpUhy9ojFvG7YseCNB6Tq2f9mg8pY'
        )

        hr_agent = Agent(
            role='Hiring Agent',
            goal='Generate targeted interview questions based on document analysis',
            backstory='Experienced hiring agent specializing in technical and professional roles',
            llm=llm,
            memory=True,
            verbose=True,
        )

        hr_questions_task = Task(
            description=f"Create a comprehensive set of interview questions based on this content: {content}",
            expected_output="A structured set of relevant interview questions",
            agent=hr_agent,
            asyn_execution=False
        )

        crew = Crew(
            agents=[hr_agent],
            tasks=[hr_questions_task],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        st.write(result.raw)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def app():
    set_custom_css()
    
    # Header
    st.title("🎯 AI Document Analyzer & Interview Assistant")
    st.markdown("Upload your document to get AI-powered analysis and interview questions.")
    
    # Configure Gemini
    genai.configure(api_key='AIzaSyBqlzrpUhy9ojFvG7YseCNB6Tq2f9mg8pY')
    
    # File Upload Section
    uploaded_file = create_file_uploader_section()
    
    if uploaded_file:
        # Document Analysis
        doc_content = process_document(uploaded_file)
        
        if doc_content:
            # Display Analysis Results
            display_analysis_results(doc_content)
            
            # Generate and Display HR Questions
            generate_hr_questions(doc_content)
            
            # Add a download button for the results
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Analysis Report",
                data=doc_content,
                file_name="analysis_report.txt",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app()