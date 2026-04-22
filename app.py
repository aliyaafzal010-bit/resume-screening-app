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
# GLASSMORPHISM UI CSS (FIXED)
# -------------------------------
st.markdown("""
<style>

/* Gradient Background */
.stApp {
    background: linear-gradient(135deg, #c7d2fe, #bbf7d0);
}

/* Glass Card */
.glass {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    color: #111827 !important;
}

/* FIX ALL TEXT VISIBILITY */
body, p, span, div, label {
    color: #111827 !important;
}

/* Streamlit text fix */
[data-testid="stMarkdownContainer"] {
    color: #111827 !important;
}

/* Headings */
h1, h2, h3, h4 {
    color: #0f172a !important;
}

/* Title */
[data-testid="stTitle"] {
    color: #0f172a !important;
}

/* Subheader */
[data-testid="stSubheader"] {
    color: #1e293b !important;
}

/* Input Fields */
input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 10px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: white !important;
    border-radius: 10px;
    padding: 10px;
}

/* Textarea */
[data-testid="stTextArea"] textarea {
    background-color: white !important;
    color: black !important;
}

/* Button */
.stButton>button {
    background: linear-gradient(to right, #2563eb, #22c55e);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
}

/* Progress bar */
.stProgress > div > div > div {
    background-color: #22c55e;
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

    st.title("💎 AI Resume Screening System")
    st.subheader("🚀 Smart AI-powered Resume Analyzer")

    st.markdown("""
    <div class="glass">
    📌 Upload your resume<br>
    📌 Paste job description<br>
    📌 Get AI-based analysis & score<br>
    📌 Improve your resume easily
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf","docx"])
    job_description = st.text_area("📝 Enter Job Description")

    if st.button("🔍 Analyze Resume"):
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

    st.title("📊 Resume Analysis Dashboard")

    text = st.session_state.data["text"]
    jd = st.session_state.data["jd"]

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    similarity = calculate_similarity(text, jd)

    jd_skills = extract_skills(jd)
    skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)

    final_score = (0.7 * similarity) + (0.3 * skill_score)

    # Extracted Info
    st.subheader("📌 Extracted Information")
    st.markdown(f"<div class='glass'>📧 Email: {email}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass'>📱 Phone: {phone}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass'>🧠 Skills: {skills}</div>", unsafe_allow_html=True)

    # Scores
    st.subheader("📈 Analysis Scores")
    st.markdown(f"<div class='glass'>📊 Similarity Score: {round(similarity,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass'>🧩 Skill Match: {round(skill_score,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass'>⭐ Final Score: {round(final_score,2)}</div>", unsafe_allow_html=True)

    st.progress(float(final_score))

    # Decision
    st.subheader("🎯 Final Decision")
    if final_score > 0.7:
        st.success("✅ Excellent Match - Highly Suitable Candidate")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match - Needs Improvement")
    else:
        st.error("❌ Poor Match - Improve Skills")

    # Suggestions
    st.subheader("💡 Improvement Suggestions")
    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.markdown(
            "<div class='glass'><b>🔧 Missing Skills:</b><br>" + ", ".join(missing_skills) + "</div>",
            unsafe_allow_html=True
        )
    else:
        st.success("🎉 Your resume matches well!")

    # Back button
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()
