import streamlit as st
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
        0% { background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); }
        50% { background: linear-gradient(135deg, #0f3460, #16213e, #1a1a2e); }
        100% { background: linear-gradient(135deg, #16213e, #1a1a2e, #0f3460); }
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
    
    .chat-input {
        background: rgba(31, 41, 55, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        margin-top: 20px;
    }

    .learning-section {
        background: rgba(31, 41, 55, 0.7);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }

    .concept-card {
        background: rgba(41, 51, 65, 0.7);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .quiz-container {
        background: rgba(31, 41, 55, 0.5);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .summary-section {
        background: rgba(41, 51, 65, 0.7);
        border-radius: 12px;
        padding: 15px;
        margin-top: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    h1, h2, h3, p {
        color: white !important;
    }

    .status-message {
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        background: rgba(25, 35, 55, 0.7);
    }
    </style>
    """, unsafe_allow_html=True)

def create_learning_agent(topic):
    llm = GoogleGenerativeAI(
        model="gemini-1.5-flash",
        verbose=True,
        temperature=0.5,
        google_api_key='AIzaSyBqlzrpUhy9ojFvG7YseCNB6Tq2f9mg8pY'
    )

    learning_agent = Agent(
        role="Learning Specialist",
        goal="Teach users about topics in an engaging and clear manner",
        verbose=True,
        memory=True,
        backstory="Expert educator specializing in breaking down complex topics into simple, understandable concepts",
        llm=llm,
        allow_delegation=False
    )

    return learning_agent

def create_learning_tasks(agent, topic):
    tasks = [
        Task(
            description=f"Explain the key concepts of {topic} in simple terms, using analogies and clear language.",
            expected_output="Clear explanation with key concepts",
            agent=agent
        ),
        Task(
            description=f"Provide 3-4 practical, real-world examples that illustrate {topic}.",
            expected_output="Relevant examples with explanations",
            agent=agent
        ),
        Task(
            description=f"Create a 5-question interactive quiz about {topic} with multiple choice answers.",
            expected_output="Interactive quiz with answers and explanations",
            agent=agent
        ),
        Task(
            description=f"Generate a concise summary of {topic} highlighting the most important takeaways.",
            expected_output="Brief, clear summary",
            agent=agent
        )
    ]
    return tasks

def display_learning_content(content):
    # Split content into sections based on common markers
    sections = content.split("Task ")
    
    for section in sections:
        if section.strip():
            # Display each section in a styled card
            st.markdown('<div class="learning-section">', unsafe_allow_html=True)
            
            # Identify and style different types of content
            if "Quiz" in section:
                st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
                st.markdown("### 📝 Knowledge Check")
                st.write(section)
                st.markdown('</div>', unsafe_allow_html=True)
            
            elif "Example" in section or "example" in section:
                st.markdown('<div class="concept-card">', unsafe_allow_html=True)
                st.markdown("### 💡 Examples")
                st.write(section)
                st.markdown('</div>', unsafe_allow_html=True)
            
            elif "Summary" in section or "summary" in section:
                st.markdown('<div class="summary-section">', unsafe_allow_html=True)
                st.markdown("### 📌 Key Takeaways")
                st.write(section)
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.write(section)
            
            st.markdown('</div>', unsafe_allow_html=True)

def app():
    set_custom_css()
    
    st.title("🎓 AI Learning Assistant")
    st.markdown("Enter any topic you'd like to learn about, and I'll help you understand it better!")

    # Initialize session state for chat history if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Chat input
    topic = st.chat_input("What would you like to learn about today?")

    if topic:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": topic})
        
        with st.spinner('Preparing your personalized learning experience...'):
            # Create learning agent and tasks
            learning_agent = create_learning_agent(topic)
            tasks = create_learning_tasks(learning_agent, topic)
            
            # Create and execute crew
            crew = Crew(
                agents=[learning_agent],
                tasks=tasks,
                verbose=True,
                process=Process.sequential
            )
            
            result = crew.kickoff()
            
            # Add assistant's response to chat history
            st.session_state.messages.append({"role": "assistant", "content": result.raw})
    
    # Display chat history with styled containers
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"**You:** {message['content']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            display_learning_content(message["content"])

if __name__ == "__main__":
    app()