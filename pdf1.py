import streamlit as st
import pdfplumber
import docx2txt
import google.generativeai as genai
import random
import json
import base64

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
    </style>
    """, unsafe_allow_html=True)

def document_upload():
    st.markdown('<div class="card-container file-uploader">', unsafe_allow_html=True)
    st.subheader("Upload Your Technical Document")
    
    docx_file = st.file_uploader(
        "Choose a file", 
        type=['txt', 'docx', 'pdf'],
        help="Supported formats: txt, docx, pdf"
    )

    if docx_file is not None:
        file_details = {
            "Filename": docx_file.name, 
            "FileType": docx_file.type, 
            "FileSize": docx_file.size
        }
        
        pdf_data = None
        if docx_file.type == "text/plain":
            pdf_data = str(docx_file.read(), "utf-8")
            st.text_area("Document Content", pdf_data, height=300)
        
        elif docx_file.type == "application/pdf":
            try:
                pdf_data = read_pdf_with_pdfplumber(docx_file)
            except:
                st.error("Error reading PDF file")
        
        elif docx_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            pdf_data = docx2txt.process(docx_file)
            st.text_area("DOCX Content", pdf_data, height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)
        return pdf_data

def read_pdf_with_pdfplumber(file):
    with pdfplumber.open(file) as pdf:
        page = pdf.pages[0]
        return page.extract_text()

def generate_interactive_mcq(content):
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.subheader("🤖 Interactive Technical Interview Questions")
    
    # Initialize session state if not exists
    if 'mcq_questions' not in st.session_state:
        # Configure Gemini AI
        genai.configure(api_key='AIzaSyBqlzrpUhy9ojFvG7YseCNB6Tq2f9mg8pY')
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""Generate 10 unique technical interview MCQ questions in the following strict JSON format:
        {{
            "questions": [
                {{
                    "question": "A precise multiple-choice technical question",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": "Correct Option",
                    "explanation": "Brief explanation of the answer"
                }}
            ]
        }}

        Base the questions on this content:
        {content}
        """
        
        with st.spinner('Generating Interactive Questions...'):
            try:
                # Multiple attempts to get a valid response
                for attempt in range(3):
                    try:
                        response = model.generate_content(prompt)
                        
                        # Find JSON within the response text
                        import re
                        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                        
                        if json_match:
                            json_str = json_match.group(0)
                            mcq_data = json.loads(json_str)
                             # Validate the parsed JSON
                            if (isinstance(mcq_data, dict) and 
                                'questions' in mcq_data and 
                                len(mcq_data['questions']) > 0):
                                break
                        
                        # If we reach here, no valid JSON was found
                        st.warning(f"Attempt {attempt + 1}: Invalid response format. Retrying...")
                    
                    except json.JSONDecodeError:
                        st.warning(f"Attempt {attempt + 1}: JSON parsing failed. Retrying...")
                else:
                    # If all attempts fail, use fallback questions
                    st.error("Failed to generate AI questions. Using predefined questions.")
                    mcq_data = {
                        "questions": [
                            {
                                "question": "What is the primary purpose of error handling in programming?",
                                "options": [
                                    "To make code look more complex", 
                                    "To prevent program crashes and manage unexpected situations", 
                                    "To increase code length", 
                                    "To slow down program execution"
                                ],
                                "correct_answer": "To prevent program crashes and manage unexpected situations",
                                "explanation": "Error handling helps manage unexpected scenarios, preventing program crashes and providing graceful error management."
                            }
                        ]
                    }
                
                # Store questions in session state
                st.session_state.mcq_questions = mcq_data['questions']
                st.session_state.mcq_score = 0
                
                # Shuffle questions
                random.shuffle(st.session_state.mcq_questions)
            
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.warning("Please try again or check your document content.")

    # Check if results should be displayed
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

    # Store user answers
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}

    questions = st.session_state.mcq_questions[:5]

    # Display questions
    for idx, q in enumerate(questions, 1):
        st.markdown(f"### Question {idx}")
        st.write(q["question"])
        
        user_answer = st.radio(f"Options for Question {idx}", q["options"], key=f"q_{idx}")
        
        if user_answer:
            st.session_state.user_answers[idx] = user_answer
        st.markdown("---")
    
    # Button to Submit
    submit_button = st.button("Submit Answers", key="submit")
    if submit_button:
        st.session_state.show_results = True

    if st.session_state.show_results:
        correct_answers = 0
        st.subheader("Results")
        for idx, q in enumerate(questions, 1):
            st.write(f"Question {idx}: {q['question']}")
            st.write(f"Your answer: {st.session_state.user_answers[idx]}")
            if st.session_state.user_answers[idx] == q["correct_answer"]:
                st.write(f"Correct Answer: {q['correct_answer']} ✅")
                correct_answers += 1
            else:
                st.write(f"Correct Answer: {q['correct_answer']} ❌")
        
        score = (correct_answers / len(questions)) * 100
        st.write(f"Your Score: {score}%")
    st.markdown('</div>', unsafe_allow_html=True)

def app():
    set_custom_css()
    st.title("AI-Based Technical Interview Assistant")
    
    pdf_data = document_upload()
    
    if pdf_data:
        generate_interactive_mcq(pdf_data)
        
if __name__ == "__main__":
    app()
