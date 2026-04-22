import streamlit as st
import pdfplumber
import docx2txt
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="centered")

# -------------------------------
# CUSTOM CSS (UI DESIGN 🔥)
# -------------------------------
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
h1 {
    color: #2c3e50;
    text-align: center;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
}
.result-box {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.title("📄 AI Resume Screening System")
st.markdown("### 🚀 Smart Resume Analyzer using AI")

# -------------------------------
# INPUT SECTION
# -------------------------------
st.markdown("## 📤 Upload Resume")
uploaded_file = st.file_uploader("", type=["pdf", "docx"])

st.markdown("## 📝 Job Description")
job_description = st.text_area("Paste Job Description Here")

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
# BUTTON
# -------------------------------
if st.button("🔍 Analyze Resume"):

    if uploaded_file and job_description:

        text = extract_text(uploaded_file)

        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)

        similarity = calculate_similarity(text, job_description)

        jd_skills = extract_skills(job_description)
        skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)

        final_score = (0.7 * similarity) + (0.3 * skill_score)

        # -------------------------------
        # OUTPUT (CARDS STYLE 🔥)
        # -------------------------------
        st.markdown("## 📊 Results")

        st.markdown(f"<div class='result-box'><b>📧 Email:</b> {email}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'><b>📱 Phone:</b> {phone}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'><b>🧠 Skills:</b> {skills}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='result-box'><b>📊 Similarity Score:</b> {round(similarity,2)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'><b>🧩 Skill Match:</b> {round(skill_score,2)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-box'><b>⭐ Final Score:</b> {round(final_score,2)}</div>", unsafe_allow_html=True)

        if final_score > 0.6:
            st.success("✅ Strong Candidate")
        else:
            st.error("❌ Not a Good Match")

    else:
        st.warning("⚠️ Please upload resume and enter job description")
 
