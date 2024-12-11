import streamlit as st
import os
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from crewai import Crew, Process, Agent, Task
from datetime import datetime
import pytz

def create_interviewer_system():
    return """You are an AI Technical Interviewer specialized in conducting detailed technical assessments.
    
    Core Functions:
    1. Ask specific questions about candidate's listed experience
    2. Deep dive into technical projects mentioned in resume
    3. Verify technical skills through practical examples
    4. Assess problem-solving using candidate's domain expertise
    
    Interview Protocol:
    - Keep questions relevant to candidate's background
    - Ask for specific examples from their experience
    - Follow up on technical details
    - Validate expertise in claimed skills
    
    Response Guidelines:
    - Reference specific resume points
    - Ask follow-up questions when needed
    - Keep tone professional but conversational
    - Focus on practical experience over theory
    """

def analyze_resume_for_keywords(resume_text):
    """Extract key technical elements from resume for question generation"""
    analysis_prompt = """
    Analyze this resume and extract:
    1. Technical skills and proficiency levels
    2. Major projects with technical details
    3. Core responsibilities in each role
    4. Technologies and tools used
    5. Industry-specific experience
    6. Notable achievements
    
    Structure the output as:
    {
        "skills": ["skill1", "skill2"...],
        "projects": [{"name": "", "tech_stack": [], "challenges": []}...],
        "responsibilities": [],
        "tools": [],
        "achievements": []
    }
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([resume_text, analysis_prompt])
    return response.text

def generate_resume_based_questions(role, experience_level, resume_analysis):
    """Generate targeted technical interview questions based on resume"""
    prompt = f"""
    Using this resume analysis: {resume_analysis}
    Create a technical interview for {role} position (Level: {experience_level}).
    
    Generate 8 questions:
    
    1. Technical Experience Questions (3):
    Format: "I see you worked with [technology from resume]. Describe a challenging problem you solved using it."
    Focus on: Major projects, technical decisions, problem-solving approaches
    
    2. Architecture & Design Questions (2):
    Format: "In [project from resume], how did you handle [specific technical challenge]?"
    Focus on: System design decisions, scalability, performance
    
    3. Problem-Solving Questions (2):
    Format: "Given your experience with [technology stack], how would you approach [relevant problem]?"
    Focus on: Real scenarios related to their experience
    
    4. Team & Communication (1):
    Format: "Tell me about explaining [technical concept from resume] to stakeholders"
    Focus on: Technical communication, team collaboration
    
    Make each question:
    - Specific to their experience
    - Focused on practical scenarios
    - Designed to reveal depth of knowledge
    
    Format each question as:
    [Category] Question
    Context: (relevant resume detail)
    Expected Discussion Points: (key areas to cover)
    Follow-up Topics: (2-3 related points to explore)
    """
    return prompt

def parse_resume_sections(resume_text):
    """Parse resume into structured sections"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    section_prompt = """
    Organize this resume into clear sections:
    1. Technical Skills & Expertise
    2. Professional Experience
    3. Projects & Achievements
    4. Education & Certifications
    
    Include specific technical details, tools, and technologies for each section.
    """
    response = model.generate_content([resume_text, section_prompt])
    return response.text

def generate_feedback(question, answer, resume_context):
    """Generate contextual feedback based on resume and answer"""
    feedback_prompt = f"""
    Question: {question}
    Answer: {answer}
    Resume Context: {resume_context}

    Provide feedback that:
    1. References relevant experience from their resume
    2. Evaluates demonstration of claimed expertise
    3. Offers constructive suggestions if needed
    4. Makes natural transition to next topic

    Keep tone professional and constructive.
    Address specific technologies/projects mentioned.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    return model.generate_content(feedback_prompt).text

def app():

    st.title("📋 Technical Interview Assessment")
    current_time = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M UTC")
    st.markdown(f"*Session started: {current_time}*")

    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.update({
            'chat_history': [],
            'current_question_index': 0,
            'interview_questions': [],
            'interview_started': False,
            'candidate_info': {},
            'resume_data': None,
            'resume_analysis': None,
            'parsed_resume': None,
            'assessment_scores': {},
            'current_phase': 'registration'
        })
        st.session_state.initialized = True

    # Configure Gemini
    genai.configure(api_key='AIzaSyBqlzrpUhy9ojFvG7YseCNB6Tq2f9mg8pY')
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Registration Phase
    if st.session_state.current_phase == 'registration':
        st.markdown("### Candidate Registration")
        with st.form("registration_form"):
            candidate_name = st.text_input("Full Name")
            candidate_email = st.text_input("Email")
            candidate_role = st.selectbox(
                "Position applying for",
                ["Software Developer", "Data Scientist", "DevOps Engineer", "ML Engineer", "Other"]
            )
            experience_level = st.selectbox(
                "Experience Level",
                ["Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior (5+ years)"]
            )
            
            uploaded_file = st.file_uploader("Upload your resume (PDF/DOC/DOCX)", type=["pdf", "doc", "docx"])
            submit_button = st.form_submit_button("Start Assessment")

            if submit_button and uploaded_file and candidate_name and candidate_email:
                st.session_state.candidate_info = {
                    'name': candidate_name,
                    'email': candidate_email,
                    'role': candidate_role,
                    'experience': experience_level,
                    'submission_time': current_time
                }
                
                # Process resume
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                temp_file_path = f"temp_file{file_extension}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                uploaded_file_path = genai.upload_file(temp_file_path)
                initial_response = model.generate_content([uploaded_file_path, "\n\n", "Extract detailed content from this resume"])
                
                if initial_response:
                    resume_text = initial_response.text
                    st.session_state.resume_data = resume_text
                    st.session_state.resume_analysis = analyze_resume_for_keywords(resume_text)
                    st.session_state.parsed_resume = parse_resume_sections(resume_text)
                    st.session_state.current_phase = 'instructions'
                    st.experimental_rerun()

    # Instructions Phase
    elif st.session_state.current_phase == 'instructions':
        st.markdown("### Technical Assessment Instructions")
        st.markdown("""
        **Guidelines:**
        1. Questions will be based on your resume and experience
        2. Provide specific examples from your work
        3. Explain technical concepts clearly
        4. Take time to think before answering
        
        **Assessment Areas:**
        - Technical expertise verification
        - Project experience deep-dive
        - Problem-solving capabilities
        - System design understanding
        - Technical communication
        
        **Duration:** 30-45 minutes
        """)
        
        if st.button("Begin Assessment"):
            llm = GoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.7,
                google_api_key='AIzaSyBqlzrpUhy9ojFvG7YseCNB6Tq2f9mg8pY'
            )

            hr_agent = Agent(
                role='Technical Interviewer',
                goal=f'Conduct technical assessment for {st.session_state.candidate_info["role"]} position',
                backstory=create_interviewer_system(),
                llm=llm
            )

            questions_task = Task(
                description=generate_resume_based_questions(
                    st.session_state.candidate_info['role'],
                    st.session_state.candidate_info['experience'],
                    st.session_state.resume_analysis
                ),
                expected_output="List of personalized technical interview questions",
                agent=hr_agent
            )

            crew = Crew(
                agents=[hr_agent],
                tasks=[questions_task],
                process=Process.sequential
            )

            result = crew.kickoff()
            st.session_state.interview_questions = [q.strip() for q in result.raw.strip().split('\n') if q]

            st.session_state.current_question_index = 0
            st.session_state.current_phase = 'interview'
            st.experimental_rerun()

    # Interview Phase
    elif st.session_state.current_phase == 'interview':
        question = st.session_state.interview_questions[st.session_state.current_question_index]
        st.markdown(f"### Question {st.session_state.current_question_index + 1}:")
        st.write(question)

        answer = st.text_area("Your Answer")
        if st.button("Submit Answer"):
            # Generate feedback after the answer is submitted
            feedback = generate_feedback(question, answer, st.session_state.resume_analysis)
            st.session_state.chat_history.append({"question": question, "answer": answer, "feedback": feedback})
            
            st.session_state.current_question_index += 1
            if st.session_state.current_question_index < len(st.session_state.interview_questions):
                st.experimental_rerun()
            else:
                st.session_state.current_phase = 'complete'
                st.experimental_rerun()

    # Completion Phase
    elif st.session_state.current_phase == 'complete':
        st.markdown("### Interview Complete")
        st.markdown("Thank you for participating! Your results will be reviewed shortly.")
        st.session_state.current_phase = 'registration'  # Reset to start over if needed

if __name__ == "__main__":
    app()
