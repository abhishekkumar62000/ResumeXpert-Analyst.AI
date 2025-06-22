# Import Important Libraries
import streamlit as st
import google.generativeai as genai # type: ignore
import webbrowser
from PyPDF2 import PdfReader # type: ignore
from docx import Document # type: ignore
from reportlab.pdfgen import canvas # type: ignore
from reportlab.lib.pagesizes import letter # type: ignore
import streamlit.components.v1 as components
from dotenv import load_dotenv  # type: ignore # Import dotenv
import os

# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="ResumeXpert Analyst", page_icon="🤖", layout="wide")

# --- Custom CSS for Enhanced Dark Neon Glassmorphism UI/UX ---
dark_neon_css = '''
<style>
body {
    background: linear-gradient(135deg, #18122B 0%, #393053 100%);
    color: #f8f8ff;
}
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(120deg, #232946 0%, #393053 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #232946 0%, #5D50FE 100%);
    color: #fff;
    border-radius: 0 20px 20px 0;
    box-shadow: 2px 0 24px #5D50FE44;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
    color: #00F2FE !important;
}
.stButton > button {
    background: linear-gradient(90deg, #5D50FE 0%, #00F2FE 100%);
    color: #fff;
    border: none;
    border-radius: 14px;
    padding: 0.7em 2em;
    font-weight: bold;
    font-size: 1.1em;
    transition: 0.2s;
    box-shadow: 0 2px 24px #00F2FE33;
    outline: 2px solid #232946;
    letter-spacing: 1px;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #00F2FE 0%, #5D50FE 100%);
    color: #fff;
    transform: scale(1.08);
    outline: 2px solid #00F2FE;
    box-shadow: 0 0 16px #00F2FE, 0 0 32px #5D50FE;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(35,41,70,0.7);
    color: #00F2FE;
    border-radius: 16px 16px 0 0;
    margin-right: 2px;
    font-weight: bold;
    font-size: 1.1em;
    border: 2px solid #5D50FE;
    border-bottom: none;
    backdrop-filter: blur(8px);
    transition: background 0.3s, color 0.3s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #5D50FE 0%, #00F2FE 100%);
    color: #fff;
    border-bottom: 4px solid #00F2FE;
    box-shadow: 0 2px 16px #00F2FE44;
}
.stTextInput > div > input, .stTextArea > div > textarea {
    background: rgba(35,41,70,0.85);
    color: #fff;
    border-radius: 10px;
    border: 2px solid #00F2FE;
    font-weight: 500;
    backdrop-filter: blur(4px);
}
.stFileUploader > label {
    color: #00F2FE;
    font-weight: bold;
}
hr {
    border: 2px solid #5D50FE;
    margin: 1.5em 0;
}
.stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: #00F2FE;
}
.stAlert {
    border-radius: 14px;
    border: 2px solid #5D50FE;
    background: rgba(35,41,70,0.85);
}
.neon-card {
    background: rgba(35,41,70,0.7);
    border-radius: 22px;
    box-shadow: 0 8px 32px 0 #00F2FE33, 0 0 0 2px #5D50FE;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 2px solid #00F2FE;
    padding: 1.7em 2.2em;
    margin-bottom: 1.5em;
    animation: neonGlow 3s infinite alternate;
}
@keyframes neonGlow {
    0% { box-shadow: 0 0 24px #00F2FE, 0 0 0 2px #5D50FE; }
    100% { box-shadow: 0 0 40px #5D50FE, 0 0 0 2px #00F2FE; }
}
</style>
'''
st.markdown(dark_neon_css, unsafe_allow_html=True)

# Add a dark neon glassmorphism animated header
st.markdown("""
<div class='neon-card' style='text-align:center;'>
    <h1 style='font-size:2.8em; margin-bottom:0; letter-spacing:2px;'>🌌ResumeXpert Analyst.AI🤖</h1>
    <p style='font-size:1.3em; margin-top:0.5em;'>Upload your resume to get detailed <span style='color:#00F2FE;'>AI feedback</span>, <span style='color:#5D50FE;'>ATS analysis</span>, and <span style='color:#00F2FE;'>job match insights</span>! 🧠</p>
    <p style='font-size:1.1em; margin-top:0.2em;'>📝 <b>Rewrite</b>. 🚀 <b>Rank</b>. 🎯 <b>Recruit</b> – <span style='color:#00F2FE;'>AI ResumeXpert</span> at Your Service! 👨‍💻</p>
</div>
""", unsafe_allow_html=True)

# Load environment variables from .env file
load_dotenv()

# Fetch API key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure the API key is set
if not GEMINI_API_KEY:
    st.error("⚠ GEMINI API Key is missing. Set it in the .env file!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

import google.api_core.exceptions  # Add this import

# List available models to verify the model name
try:
    available_models = genai.list_models()
    model_names = [model.name for model in available_models]
    
    # Verify if the desired model is in the list
    desired_model_name = "models/gemini-1.5-flash-latest"  # Replace with the correct model name
    if desired_model_name in model_names:
        model = genai.GenerativeModel(desired_model_name)
    else:
        st.error(f"⚠ Model '{desired_model_name}' not found. Available models: {model_names}")
        st.stop()
except google.api_core.exceptions.PermissionDenied as e:
    st.error("⚠ Permission denied. Please check your API key permissions.")
    st.stop()
except google.api_core.exceptions.InvalidArgument as e:
    st.error("⚠ Invalid argument. Please check the model name and API key.")
    st.stop()
except Exception as e:
    st.error(f"⚠ An unexpected error occurred: {e}")
    st.stop()

def chat_with_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text if response else "No response received."
    except google.api_core.exceptions.NotFound as e:
        st.error("⚠ Model not found. Please check the model name and API key.")
        return "Model not found."
    except google.api_core.exceptions.PermissionDenied as e:
        st.error("⚠ Permission denied. Please check your API key permissions.")
        return "Permission denied."
    except google.api_core.exceptions.InvalidArgument as e:
        st.error("⚠ Invalid argument. Please check the model name and API key.")
        return "Invalid argument."
    except Exception as e:
        st.error(f"⚠ An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"

# Your other code remains the same
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.run(asyncio.sleep(0))  # ✅ Ensure a running event loop

# UI Improvements
AI_path = "AI.png"  # Ensure this file is in the same directory as your script
try:
    st.sidebar.image(AI_path, use_container_width=True)
except FileNotFoundError:
    st.sidebar.warning("AI.png file not found. Please check the file path.")

image_path = "image.png"  # Ensure this file is in the same directory as your script
try:
    st.sidebar.image(image_path, use_container_width=True)
except FileNotFoundError:
    st.sidebar.warning("image.png file not found. Please check the file path.")

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%); padding: 1em; border-radius: 12px; margin-bottom: 1em; box-shadow: 0 2px 12px rgba(221,36,118,0.12);'>
        <h2 style='color: #fff; text-align: center; margin-bottom: 0.5em;'>⚙ App Features</h2>
    </div>
    """, unsafe_allow_html=True)
    tab_selection = st.radio("Select a Feature:", [
        "📄 Resume Analysis",
        "📊 ATS Score & Fixes",
        "💼 Job Fit Analysis",
        "🚀 AI Project Suggestions",
        "💡 Best Career Path",
        "🛠 Missing Skills & Learning Guide",
        "🎓 Certifications & Courses",
        "💰 Expected Salaries & Job Roles",
        "📊 AI Resume Ranking",
        "🔍 Personalized Job Alerts",
        "✉ AI Cover Letter Generator",
        "🎤 AI Mock Interviews"
    ])
    st.markdown("""
    <div style='background: #232526; padding: 0.7em; border-radius: 10px; margin-top: 1em; text-align: center;'>
        <span style='color: #fff; font-size: 1.1em;'>👨‍💻 <b>Developer:</b> <span style='color:#ff512f;'>Abhishek❤Yadav</span></span>
    </div>
    """, unsafe_allow_html=True)
    # Add developer picture below the developer name
    try:
        st.image('pic.jpg', width=280, caption='Abhishek Yadav', use_container_width=False)
    except Exception:
        st.warning('Developer image not found (pic.jpg).')

def extract_text(file):
    if file.name.endswith(".pdf"):
        pdf_reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "❌ Unsupported file format. Upload a PDF or DOCX."

def analyze_resume(text):
    prompt = f"""
    You are an expert AI Resume Reviewer. Analyze the following resume thoroughly and provide structured insights on:
    0️⃣ first Full Detail Analysis of Resume Files and Display all details of the resume
    1️⃣ Strengths: What makes this resume stand out? Identify key skills, achievements, and formatting positives.
    2️⃣ Areas for Improvement: Highlight missing elements, weak points, and vague descriptions that need enhancement.
    3️⃣ Formatting Suggestions: Provide recommendations for a more professional and ATS-compliant structure.
    4️⃣ ATS Compliance Check: Analyze the resume for ATS-friendliness, including keyword optimization and readability.
    5️⃣ Overall Rating: Score the resume on a scale of 1 to 10 with justification.
    
    Resume:
    {text}
    """
    return chat_with_gemini(prompt)

def match_job_description(resume_text, job_desc):
    prompt = f"""
    You are an AI Job Fit Analyzer. Compare the given resume with the provided job description and generate a structured report:
    
    ✅ Matching Skills: Identify skills in the resume that match the job description.
    ❌ Missing Skills: Highlight missing key skills that the candidate needs to acquire.
    📊 Fit Percentage: Provide a percentage match score based on skillset, experience, and qualifications.
    🏆 Final Verdict: Clearly state whether the candidate is a "Good Fit" or "Needs Improvement" with reasons.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_desc}
    """
    return chat_with_gemini(prompt)

def get_resume_score(resume_text):
    prompt = f"""
    As an AI Resume Scorer, evaluate the resume across different factors and provide a structured breakdown:
    
    🎯 Skills Match: XX% (How well the skills align with industry requirements)
    📈 Experience Level: XX% (Assessment of experience depth and relevance)
    ✨ Formatting Quality: XX% (Resume structure, clarity, and ATS compliance)
    🔍 Overall Strength: XX% (General effectiveness of the resume)
    
    Provide the final Resume Score (0-100) with a breakdown and actionable insights for improvement.
    
    Resume:
    {resume_text}
    """
    return chat_with_gemini(prompt)

def get_improved_resume(resume_text):
    prompt = f"""
    Optimize the following resume to enhance its professionalism, clarity, and ATS compliance:
    
    - ✅ Fix grammar and spelling errors
    - 🔥 Improve clarity, conciseness, and professionalism
    - ✨ Optimize formatting for readability and ATS-friendliness
    - 📌 Ensure keyword optimization to improve job match chances
    - 🏆 Enhance overall presentation while maintaining content integrity
    
    Resume:
    {resume_text}
    
    Provide only the improved resume text.
    """
    return chat_with_gemini(prompt)

def create_pdf(text, filename="Optimized_Resume.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(50, 750, text)
    c.save()
    return filename

# Create Section-wise Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📂 Upload Resume", "📊 Job Match Analysis", "🚀 AI Project Suggestions", "🤷‍♂ ATS Score Checker", "📊 AI-Powered Resume Ranking"])

# Tab 1: Resume Upload and Analysis
with tab1:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(221,36,118,0.10);'>
        <h2 style='color: #fff; margin: 0;'>📂 Upload Resume</h2>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        st.success("✅ Resume Uploaded Successfully!")
        resume_text = extract_text(uploaded_file)
        
        # AI Resume Analysis
        feedback = analyze_resume(resume_text)
        score_feedback = get_resume_score(resume_text)

        st.subheader("📝 AI Feedback")
        st.write(feedback)
        
        st.subheader("⭐ Resume Score & ATS Breakdown")
        st.write(score_feedback)
        
        if st.button("🚀 Improve Resume & Download"):
            improved_resume_text = get_improved_resume(resume_text)
            updated_pdf = create_pdf(improved_resume_text)
            st.success("🎉 Resume Improved Successfully!")
            st.download_button("⬇ Download Optimized Resume", open(updated_pdf, "rb"), file_name="Optimized_Resume.pdf")

# Tab 2: Job Match Analysis
with tab2:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #36d1c4 0%, #5b86e5 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(91,134,229,0.10);'>
        <h2 style='color: #fff; margin: 0;'>📊 Job Match Analysis</h2>
    </div>
    """, unsafe_allow_html=True)
    job_desc = st.text_area("📌 Paste Job Description Here:")
    if job_desc and 'resume_text' in locals():
        st.write("🔍 Analyzing job fit...")
        job_fit_feedback = match_job_description(resume_text, job_desc)
        st.subheader("📊 Job Fit Analysis")
        st.write(job_fit_feedback)

# Function to Generate AI-Based Project Suggestions (5 per level)
def suggest_projects(resume_text):
    prompt = f"""
    You are a project mentor Expert. Based on the resume below, suggest 5 projects for each level:
    
    Basic Level (For Beginners): 5 easy projects to get started.  
    Intermediate Level (For Practitioners): 5 projects requiring more expertise.  
    Advanced Level (For Experts): 5 complex projects showcasing deep skills.  
    
    🔹 For Each Project: Provide a brief description and the required tech stack (tools, frameworks, technologies).  
    🔹 Make sure the projects align with the user's skills, experience, and domain.  
    
    Resume:
    {resume_text}
    """
    return chat_with_gemini(prompt)

# Tab 3: AI Project Suggestions
with tab3:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(221,36,118,0.10);'>
        <h2 style='color: #fff; margin: 0;'>🚀 AI Project Suggestions</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("🚀 AI-Powered Project Suggestions")
    if uploaded_file and 'resume_text' in locals():
        if st.button("📌 Get Project Ideas Based on Resume"):
            project_suggestions = suggest_projects(resume_text)
            st.write(project_suggestions)

# Function to Calculate ATS Score & Provide Feedback
def check_ats_score(resume_text):
    prompt = f"""
    You are an ATS resume evaluator. Based on the resume below, analyze its ATS compatibility on a scale of 100. 
    
    Scoring Criteria:  
    - ✅ Proper Formatting & Readability (20%)  
    - ✅ Use of Correct Keywords (30%)  
    - ✅ Section Organization (20%)  
    - ✅ No Unnecessary Graphics or Tables (15%)  
    - ✅ Proper Contact Info & Structure (15%)  
    
    Provide Output as:  
    - ATS Score (out of 100)
    - Improvement Suggestions to improve 100 ATS Score
    
    Resume:
    {resume_text}
    """
    response = chat_with_gemini(prompt)
    try:
        ats_score = int(response.split("ATS Score:")[1].split("/100")[0].strip())
    except (IndexError, ValueError):
        ats_score = 0  # Default to 0 if parsing fails
    ats_feedback = response.split("Improvement Suggestions to improve 100 ATS Score")[1].strip() if "Improvement Suggestions to improve 100 ATS Score" in response else "No feedback available."
    return ats_score, ats_feedback

# Tab 4: ATS Score Checker
with tab4:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #36d1c4 0%, #5b86e5 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(91,134,229,0.10);'>
        <h2 style='color: #fff; margin: 0;'>🤷‍♂ ATS Score Checker</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("🤷‍♂ ATS Score Checker")
    
    if uploaded_file and 'resume_text' in locals():
        if st.button("🔍 Check ATS Score"):
            ats_score, ats_feedback = check_ats_score(resume_text)
            st.markdown(f"### ✅ Your ATS Score: {ats_score}/100")
            if ats_score < 80:
                st.warning("⚠ Your resume needs improvement!")
                st.write(ats_feedback)
            else:
                st.success("🎉 Your resume is ATS-friendly!")

# Tab 5: AI-Powered Resume Ranking
with tab5:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(221,36,118,0.10);'>
        <h2 style='color: #fff; margin: 0;'>📊 AI-Powered Resume Ranking</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("📊 AI-Powered Resume Ranking")

    # Upload multiple resume files
    uploaded_files = st.file_uploader("Upload Multiple Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

    # Process resumes if uploaded
    if uploaded_files:
        resume_texts = []
        file_names = []
        
        for file in uploaded_files:
            text = extract_text(file)  # Function to extract text from PDF/DOCX
            if text.startswith("❌"):  # Error handling
                st.error(f"❌ Unable to process: {file.name}")
            else:
                resume_texts.append(text)
                file_names.append(file.name)

        if len(resume_texts) > 0:
            if st.button("🚀 Rank Resumes"):  # Button to rank resumes
                ranked_resumes = []
                
                for i, text in enumerate(resume_texts):
                    rank_prompt = f"""
                    You are an AI Resume Evaluator. Assess the following resume based on:
                    ✅ *ATS Compatibility*
                    ✅ *Readability & Formatting*
                    ✅ *Job Fit & Skills Alignment*
                    
                    Give a *score out of 100* and a brief analysis.

                    Resume:
                    {text}
                    """
                    score_response = chat_with_gemini(rank_prompt)  # AI function to analyze resume
                    try:
                        score = int(score_response.split("Score:")[-1].split("/")[0].strip())  # Extract score
                    except (IndexError, ValueError):
                        score = 0  # Default to 0 if parsing fails
                    ranked_resumes.append((file_names[i], score))

                # Sort resumes by score (Highest to Lowest)
                ranked_resumes.sort(key=lambda x: x[1], reverse=True)

                # Display ranked results
                st.subheader("🏆 Ranked Resumes")
                for i, (name, score) in enumerate(ranked_resumes, start=1):
                    st.write(f"{i}. {name}** - *Score: {score}/100*")

# Creating multiple tabs together
tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "💡 AI Career Roadmap & Skills Guide",
    "🛠 Missing Skills & How to Learn Them",
    "📜 Certifications & Course Recommendations",
    "💰 Expected Salaries & Job Roles",
    "📢 Resume Feedback via AI Chat",
    "📢 Personalized Job Alerts",
    "💡 Soft Skills Analysis & Improvement"
])

# Tab 6: Best Career Path
with tab6:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #36d1c4 0%, #5b86e5 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(91,134,229,0.10);'>
        <h2 style='color: #fff; margin: 0;'>💡 AI Career Roadmap & Skills Guide</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("💡 AI Career Roadmap & Skills Guide")
    if uploaded_file and 'resume_text' in locals():
        if st.button("🚀 Get Career Insights"):
            def generate_career_roadmap(resume_text):
                prompt = f"""
                You are an AI Career Advisor. Based on the following resume, suggest the best career path:

                ✅ Current Strengths & Skills: Identify the user's key strengths.
                🚀 Best Career Path: Recommend an ideal career direction.
                📈 Career Growth Roadmap:
                   - 🔹 Entry-Level Roles
                   - 🔸 Mid-Level Roles
                   - 🔺 Senior-Level Roles
                🔮 Future Industry Trends: Emerging trends & opportunities.

                Resume:
                {resume_text}
                """
                return chat_with_gemini(prompt)

            career_guidance = generate_career_roadmap(resume_text)
            st.write(career_guidance)

# Tab 7: Missing Skills
with tab7:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(221,36,118,0.10);'>
        <h2 style='color: #fff; margin: 0;'>🛠 Missing Skills & How to Learn Them</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("🛠 Missing Skills & How to Learn Them")
    if uploaded_file and 'resume_text' in locals():
        if st.button("📚 Identify Missing Skills"):
            def find_missing_skills(resume_text):
                prompt = f"""
                You are an AI Skill Analyzer. Analyze the following resume and provide missing skills:

                ✅ Existing Skills: List the current skills of the user.
                ❌ Missing Skills: Identify skills required for industry standards.
                🎯 How to Learn Them: Provide learning resources (courses, books, projects).
                🔥 Importance of These Skills: Explain how these skills will improve job opportunities.

                Resume:
                {resume_text}
                """
                return chat_with_gemini(prompt)

            missing_skills = find_missing_skills(resume_text)
            st.write(missing_skills)

# Tab 8: Certifications & Courses
with tab8:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #36d1c4 0%, #5b86e5 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(91,134,229,0.10);'>
        <h2 style='color: #fff; margin: 0;'>📜 Certifications & Course Recommendations</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("📜 Certifications & Course Recommendations")
    if uploaded_file and 'resume_text' in locals():
        if st.button("🎓 Get Course Recommendations"):
            def recommend_certifications(resume_text):
                prompt = f"""
                You are an AI Career Coach. Analyze the following resume and suggest relevant certifications & courses:

                ✅ Top 5 Certifications: Industry-recognized certifications that align with the user’s skills and career path.
                📚 Top 5 Online Courses: From platforms like Coursera, Udemy, LinkedIn Learning, or edX.
                🔥 Why These Certifications?: Explain why these certifications/courses will boost their career.
                🛠 Preparation Resources: Provide book or website recommendations.

                Resume:
                {resume_text}
                """
                return chat_with_gemini(prompt)

            courses = recommend_certifications(resume_text)
            st.write(courses)

# Tab 9: Expected Salaries & Job Roles
with tab9:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #ff512f 0%, #dd2476 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px rgba(221,36,118,0.10);'>
        <h2 style='color: #fff; margin: 0;'>💰 Expected Salaries & Job Roles</h2>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("💰 Expected Salaries & Job Roles")
    if uploaded_file and 'resume_text' in locals():
        if st.button("💼 Get Salary & Job Role Insights"):
            def get_salary_and_jobs(resume_text):
                prompt = f"""
                You are an AI Career Consultant. Analyze the following resume and provide structured salary insights:

                💼 Best Job Roles: Suggest top job roles based on user’s skills, experience, and industry trends.
                🌎 Salary Estimates by Region:
                   - USA: $XX,XXX - $XX,XXX per year
                   - UK: £XX,XXX - £XX,XXX per year
                   - India: ₹XX,XX,XXX - ₹XX,XX,XXX per year
                   - Remote/Global: $XX,XXX per year (varies based on employer)
                📈 Career Growth Insights: How salaries and opportunities increase with upskilling.
                🔥 Top Industries Hiring: Which industries are in demand for the user's skills?

                Resume:
                {resume_text}
                """
                return chat_with_gemini(prompt)

            salary_and_jobs = get_salary_and_jobs(resume_text)
            st.write(salary_and_jobs)


# Tab 10: Interactive Resume Q&A
with tab10:
    st.subheader("📢 Ask AI About Your Resume")
    st.markdown("💬 Type any question about your resume, and AI will provide detailed guidance!")

    if uploaded_file:
        user_question = st.text_input("❓ Ask anything about your resume:")
        
        if user_question:
            with st.spinner("🤖 AI is analyzing your resume..."):
                prompt = f"""
                You are an expert AI Resume Consultant. A user has uploaded their resume and is asking the following question:

                Question: {user_question}
                
                Resume: 
                {resume_text}

                Provide a detailed, structured, and insightful response, including:
                - Key observations from their resume.
                - Actionable improvements tailored to their experience.
                - Industry best practices for better job opportunities.
                """
                response = chat_with_gemini(prompt)
                st.write("💡 AI Response:")
                st.write(response)

# Tab 11: Personalized Job Alerts
with tab11:
    st.subheader("🔔 Personalized Job Alerts")

    # Input fields for user preferences
    job_title = st.text_input("🎯 Enter Job Title (e.g., Data Scientist, Software Engineer)")
    location = st.text_input("📍 Preferred Location (e.g., Remote, New York, Bangalore)")
    
    if st.button("🔍 Find Jobs Now"):
        if job_title and location:
            st.success(f"🔗 Here are job links for *{job_title}* in *{location}*:")

            # Dynamic job search URLs
            indeed_url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location.replace(' ', '+')}"
            linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={job_title.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            naukri_url = f"https://www.naukri.com/{job_title.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
            google_jobs_url = f"https://www.google.com/search?q={job_title.replace(' ', '+')}+jobs+in+{location.replace(' ', '+')}"

            # Display clickable job links
            st.markdown(f"[🟢 Indeed Jobs]({indeed_url})")
            st.markdown(f"[🔵 LinkedIn Jobs]({linkedin_url})")
            st.markdown(f"[🟠 Naukri Jobs]({naukri_url})")
            st.markdown(f"[🔴 Google Jobs]({google_jobs_url})")

            # Open default browser with job search links
            webbrowser.open(indeed_url)
            webbrowser.open(linkedin_url)
            webbrowser.open(naukri_url)
            webbrowser.open(google_jobs_url)
        else:
            st.error("⚠ Please enter both job title and location to get job alerts.")

# Tab 12: Soft Skills Analysis & Improvement Tips
with tab12:
    st.subheader("💡 Soft Skills Analysis & Improvement")

    if uploaded_file:
        resume_text = extract_text(uploaded_file)  # Ensure resume_text is defined
        soft_skills_prompt = f"""
        You are an AI Soft Skills Analyzer. Based on the resume, identify the candidate's *soft skills* and suggest ways to improve them:
        
        ✅ *Identified Soft Skills*
        ✅ *Why these skills are important*
        ✅ *Recommended activities to strengthen them*
        ✅ *Online courses or books to improve them*
        
        Resume:
        {resume_text}
        """
        if st.button("📚 Get Soft Skills Insights"):
            soft_skills_analysis = chat_with_gemini(soft_skills_prompt)
            st.write(soft_skills_analysis)
    else:
        st.warning("Please upload a resume to analyze soft skills.")

# --- Enhanced Tab: AI Interview Simulator, Portfolio & GitHub Review, AI Networking Suggestions ---
interview_tab, portfolio_tab, networking_tab = st.tabs([
    "🎤 AI Interview Simulator",
    "💻 Portfolio & GitHub Review",
    "🤝 AI Networking Suggestions"
])

# AI Interview Simulator
with interview_tab:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #5D50FE 0%, #00F2FE 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px #00F2FE33;'>
        <h2 style='color: #fff; margin: 0;'>🎤 AI Interview Simulator</h2>
    </div>
    """, unsafe_allow_html=True)
    st.write("Practice with AI-generated interview questions, get instant feedback, and receive a full interview report!")
    if 'uploaded_file' in locals() and uploaded_file:
        resume_text = extract_text(uploaded_file)
        st.markdown("**Step 1: Interview Settings**")
        interview_type = st.selectbox("Select Interview Type", ["Technical", "HR", "Behavioral", "Custom"])
        num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
        job_desc = st.text_area("(Optional) Paste Job Description for Targeted Questions:")
        custom_topic = ""
        if interview_type == "Custom":
            custom_topic = st.text_input("Enter Custom Interview Topic (e.g., Data Science, Leadership)")
        if st.button("🎤 Generate Interview Questions") or 'interview_questions' in st.session_state:
            if 'interview_questions' not in st.session_state:
                topic = custom_topic if interview_type == "Custom" else interview_type
                interview_prompt = f"""
                You are an AI interviewer. Generate {num_questions} {topic} interview questions based on the candidate's resume and the job description (if provided). Number each question. Keep questions concise and relevant.
                Resume:
                {resume_text}
                Job Description:
                {job_desc}
                """
                questions_text = chat_with_gemini(interview_prompt)
                # Parse questions into a list
                import re
                questions = re.findall(r"\d+\.\s*(.*)", questions_text)
                if not questions:
                    questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
                st.session_state['interview_questions'] = questions[:num_questions]
                st.session_state['answers'] = [""] * len(st.session_state['interview_questions'])
                st.session_state['feedbacks'] = [""] * len(st.session_state['interview_questions'])
                st.session_state['current_q'] = 0
            questions = st.session_state['interview_questions']
            answers = st.session_state['answers']
            feedbacks = st.session_state['feedbacks']
            current_q = st.session_state['current_q']
            st.markdown(f"**Question {current_q+1} of {len(questions)}:**")
            st.markdown(f"> {questions[current_q]}")
            answer = st.text_area("Your Answer", value=answers[current_q], key=f"answer_{current_q}")
            if st.button("💡 Get Instant Feedback", key=f"feedback_btn_{current_q}"):
                feedback_prompt = f"""
                You are an AI interviewer. Here is the candidate's answer to the following question. Give detailed, constructive feedback and a score out of 10.
                Question: {questions[current_q]}
                Answer: {answer}
                """
                feedback = chat_with_gemini(feedback_prompt)
                feedbacks[current_q] = feedback
                answers[current_q] = answer
                st.session_state['answers'] = answers
                st.session_state['feedbacks'] = feedbacks
            if feedbacks[current_q]:
                st.info(feedbacks[current_q])
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("⬅ Previous", key=f"prev_{current_q}") and current_q > 0:
                    st.session_state['current_q'] -= 1
            with col2:
                if st.button("➡ Next", key=f"next_{current_q}") and current_q < len(questions)-1:
                    st.session_state['answers'][current_q] = answer
                    st.session_state['current_q'] += 1
            with col3:
                if st.button("🏁 Finish Interview"):
                    st.session_state['answers'][current_q] = answer
                    st.session_state['interview_finished'] = True
            # Show summary if finished
            if st.session_state.get('interview_finished', False):
                st.markdown("---")
                st.markdown("## 📝 Interview Summary Report")
                summary_prompt = f"""
                You are an AI interview coach. Analyze the following Q&A and feedback. Give a summary with:
                - Strengths
                - Areas for Improvement
                - Overall Interview Readiness Score (0-100)
                - Motivational closing remark
                Q&A and Feedback:
                """
                for i, q in enumerate(questions):
                    summary_prompt += f"\nQ{i+1}: {q}\nA: {answers[i]}\nFeedback: {feedbacks[i]}"
                summary = chat_with_gemini(summary_prompt)
                st.success(summary)
                # Download report
                if st.button("⬇ Download Interview Report"):
                    report_text = f"Interview Questions and Answers\n\n"
                    for i, q in enumerate(questions):
                        report_text += f"Q{i+1}: {q}\nA: {answers[i]}\nFeedback: {feedbacks[i]}\n\n"
                    report_text += f"\nSummary:\n{summary}"
                    filename = create_pdf(report_text, filename="Interview_Report.pdf")
                    st.download_button("Download Report as PDF", open(filename, "rb"), file_name="Interview_Report.pdf")
    else:
        st.info("Upload a resume to use the enhanced interview simulator.")

# Portfolio & GitHub Integration
with portfolio_tab:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #232946 0%, #5D50FE 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px #5D50FE33;'>
        <h2 style='color: #fff; margin: 0;'>💻 Portfolio & GitHub Integration</h2>
    </div>
    """, unsafe_allow_html=True)
    st.write("Link your GitHub or portfolio to get AI-powered project/code review and suggestions!")
    github_username = st.text_input("Enter your GitHub username (public repos only):")
    portfolio_url = st.text_input("Enter your portfolio URL (optional):")
    colA, colB = st.columns([2,1])
    with colA:
        analyze_btn = st.button("🔍 Analyze My Projects", key="analyze_projects_btn")
    with colB:
        example_btn = st.button("🧪 Test with Example (octocat)", key="test_octocat_btn")
    if analyze_btn or example_btn:
        import requests
        if example_btn:
            github_username = "octocat"
        if github_username:
            github_api = f"https://api.github.com/users/{github_username}/repos"
            st.info(f"🔗 GitHub API URL: [Click to check in browser]({github_api})")
            with st.spinner("Fetching GitHub data..."):
                resp = requests.get(github_api)
                if resp.status_code == 200:
                    repos = resp.json()
                    if not repos:
                        st.warning("No public repositories found for this username.")
                    else:
                        st.markdown("**Your Public GitHub Projects:**")
                        for repo in repos:
                            with st.expander(f"{repo['name']}"):
                                st.write(f"Description: {repo.get('description','No description')}")
                                st.write(f"⭐ Stars: {repo.get('stargazers_count',0)} | 🍴 Forks: {repo.get('forks_count',0)}")
                                st.write(f"🔗 [View Repo]({repo['html_url']})")
                        repo_descs = [f"{repo['name']}: {repo.get('description','') or 'No description'}" for repo in repos]
                        ai_review_prompt = f"""
                        You are an expert AI code reviewer. Here are the user's public GitHub projects:\n{repo_descs}\nPortfolio URL: {portfolio_url}\n\nAnalyze the projects for:\n- Technical strengths\n- Areas for improvement\n- Suggestions for new projects or skills\n- How to make the portfolio more impressive\nGive a detailed, actionable review.
                        """
                        ai_review = chat_with_gemini(ai_review_prompt)
                        st.markdown("---")
                        st.subheader("🤖 AI Review & Suggestions")
                        st.write(ai_review)
                else:
                    try:
                        error_msg = resp.json().get('message', '')
                    except Exception:
                        error_msg = resp.text
                    st.error(f"❌ Could not fetch GitHub data. Status code: {resp.status_code}. {error_msg}\n\n**Tips:**\n- Double-check your username.\n- Make sure you have public repos.\n- Try opening the [API URL]({github_api}) in your browser.\n- If using a company/org account, check permissions.")
        else:
            st.warning("Please enter your GitHub username.")

# AI-Powered Networking Suggestions
with networking_tab:
    st.markdown("""
    <div style='background: linear-gradient(90deg, #36d1c4 0%, #5b86e5 100%); padding: 0.7em 1em; border-radius: 10px; margin-bottom: 1em; box-shadow: 0 2px 8px #36d1c433;'>
        <h2 style='color: #fff; margin: 0;'>🤝 AI-Powered Networking Suggestions</h2>
    </div>
    """, unsafe_allow_html=True)
    st.write("Get personalized networking tips, LinkedIn/community suggestions, and a ready-to-use outreach message!")
    career_goal = st.text_input("Your Career Goal / Target Role (e.g., Data Scientist, Product Manager)")
    skills = st.text_input("Key Skills (comma separated)")
    networking_btn = st.button("🔗 Get Networking Suggestions", key="networking_suggestions_btn")
    if networking_btn:
        if career_goal:
            networking_prompt = f"""
            You are an AI career networking coach. Based on the user's career goal and skills, suggest:\n- 3 LinkedIn connection types (roles, industries, or people)\n- 3 relevant online communities or groups\n- 2-3 potential mentor profiles (describe the type, not real people)\n- 5 actionable networking tips\n- A personalized LinkedIn outreach message template\n\nCareer Goal: {career_goal}\nSkills: {skills}
            """
            networking_suggestions = chat_with_gemini(networking_prompt)
            st.markdown("---")
            st.subheader("🤖 AI Networking Suggestions")
            st.write(networking_suggestions)
        else:
            st.warning("Please enter your career goal.")

# Move the Chatbase Chatbot to the bottom of the script
chatbase_script = """
<script>
(function(){if(!window.chatbase||window.chatbase("getState")!=="initialized"){window.chatbase=(...arguments)=>{if(!window.chatbase.q){window.chatbase.q=[]}window.chatbase.q.push(arguments)};window.chatbase=new Proxy(window.chatbase,{get(target,prop){if(prop==="q"){return target.q}return(...args)=>target(prop,...args)}})}const onLoad=function(){const script=document.createElement("script");script.src="https://www.chatbase.co/embed.min.js";script.id="bY0i_WqBGZxHKIOpFSAsS";script.domain="www.chatbase.co";document.body.appendChild(script)};if(document.readyState==="complete"){onLoad()}else{window.addEventListener("load",onLoad)}})();
</script>
"""

# Display Chatbase Chatbot at the bottom of the app
st.markdown("---")  # Add a horizontal line for separation
st.header("💬 Chat with AI")
components.html(chatbase_script, height=600)
