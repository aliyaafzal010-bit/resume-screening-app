import streamlit as st
import pdfplumber
import docx2txt
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# -------------------------------
# CUSTOM CSS (PRO UI 🔥)
# -------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #6a11cb, #2575fc);
}
.main {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 15px;
}
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FUNCTIONS
# -------------------------------
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        text = docx2txt.process(file)
    return text

def extract_email(text):
    return re.findall(r'\S+@\S+', text)

def extract_phone(text):
    return re.findall(r'\b\d{10}\b', text)

skills_db = [
    "python","java","sql","machine learning","ai",
    "data science","deep learning","html","css","javascript"
]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_db if skill in text]

def calculate_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume, jd])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

# -------------------------------
# SESSION STATE
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------------------
# HOME PAGE
# -------------------------------
if st.session_state.page == "home":

    st.title("🚀 AI Resume Screening System")
    st.markdown("### ✨ Smart AI Tool for Resume Analysis")

    st.write("""
    This application helps HR teams and recruiters analyze resumes automatically.
    
    🔹 Upload your resume  
    🔹 Enter job description  
    🔹 Get AI-based match score  
    🔹 Get improvement suggestions  
    """)

    uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf","docx"])
    job_description = st.text_area("📝 Enter Job Description")

    if st.button("➡️ Analyze Resume"):

        if uploaded_file and job_description:

            text = extract_text(uploaded_file)

            st.session_state.data = {
                "text": text,
                "jd": job_description
            }

            st.session_state.page = "analysis"
            st.rerun()

        else:
            st.warning("⚠️ Please upload resume and enter job description")

# -------------------------------
# ANALYSIS PAGE
# -------------------------------
elif st.session_state.page == "analysis":

    st.title("📊 Resume Analysis Report")

    text = st.session_state.data["text"]
    jd = st.session_state.data["jd"]

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    similarity = calculate_similarity(text, jd)

    jd_skills = extract_skills(jd)
    skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)

    final_score = (0.7 * similarity) + (0.3 * skill_score)

    # -------------------------------
    # DISPLAY DATA
    # -------------------------------
    st.markdown("### 📌 Extracted Information")

    st.markdown(f"<div class='card'>📧 Email: {email}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>📱 Phone: {phone}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>🧠 Skills: {skills}</div>", unsafe_allow_html=True)

    st.markdown("### 📈 Analysis Scores")

    st.markdown(f"<div class='card'>📊 Similarity Score: {round(similarity,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>🧩 Skill Match: {round(skill_score,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>⭐ Final Score: {round(final_score,2)}</div>", unsafe_allow_html=True)

    # -------------------------------
    # RESULT DECISION
    # -------------------------------
    st.markdown("### 🎯 Final Decision")

    if final_score > 0.7:
        st.success("✅ Excellent Match - Candidate is highly suitable!")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match - Candidate can improve")
    else:
        st.error("❌ Poor Match - Needs significant improvement")

    # -------------------------------
    # IMPROVEMENT SUGGESTIONS
    # -------------------------------
    st.markdown("### 💡 Improvement Suggestions")

    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.write("🔧 Add these skills to improve your resume:")
        st.write(missing_skills)
    else:
        st.write("🎉 Your resume matches well with the job!")

    # Back button
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()
 
