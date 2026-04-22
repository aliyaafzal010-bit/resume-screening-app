import streamlit as st
import pdfplumber
import docx2txt
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# -------------------------------
# 🎨 CLEAN MODERN UI
# -------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #e0e7ff, #f0fdf4);
}

/* Main card */
.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

/* Score card */
.score {
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    color: #4f46e5;
}

/* Headings */
h1, h2, h3 {
    color: #111827 !important;
}

/* Button */
.stButton>button {
    background: #4f46e5;
    color: white;
    border-radius: 10px;
}

/* File uploader fix */
[data-testid="stFileUploader"] {
    background: #111827;
    padding: 10px;
    border-radius: 10px;
}
[data-testid="stFileUploader"] * {
    color: white !important;
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

def extract_skills(text):
    skills_db = ["python","java","sql","machine learning","ai","data science","html","css"]
    text = text.lower()
    return [s for s in skills_db if s in text]

def calculate_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume, jd])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

# -------------------------------
# SESSION
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------------------
# HOME
# -------------------------------
if st.session_state.page == "home":

    st.title("💎 AI Resume Analyzer")

    st.markdown('<div class="card">Upload your resume and get instant ATS score</div>', unsafe_allow_html=True)

    file = st.file_uploader("Upload Resume", type=["pdf","docx"])
    jd = st.text_area("Paste Job Description")

    if st.button("Analyze"):
        if file and jd:
            text = extract_text(file)
            st.session_state.data = {"text": text, "jd": jd}
            st.session_state.page = "analysis"
            st.rerun()
        else:
            st.warning("Upload file and enter JD")

# -------------------------------
# ANALYSIS
# -------------------------------
else:

    text = st.session_state.data["text"]
    jd = st.session_state.data["jd"]

    skills = extract_skills(text)
    jd_skills = extract_skills(jd)

    similarity = calculate_similarity(text, jd)
    skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)
    final_score = round((0.7 * similarity) + (0.3 * skill_score), 2)

    st.title("📊 Analysis Dashboard")

    # 🎯 SCORE (MAIN FOCUS)
    st.markdown(f'<div class="card"><div class="score">{int(final_score*100)}%</div><center>ATS Match Score</center></div>', unsafe_allow_html=True)

    # 📌 Skills
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card"><b>Your Skills</b><br>' + ", ".join(skills) + '</div>', unsafe_allow_html=True)

    with col2:
        missing = list(set(jd_skills) - set(skills))
        st.markdown('<div class="card"><b>Missing Skills</b><br>' + ", ".join(missing) + '</div>', unsafe_allow_html=True)

    # 🎯 Decision
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if final_score > 0.7:
        st.success("Excellent Match 🎉")
    elif final_score > 0.5:
        st.warning("Moderate Match ⚠️")
    else:
        st.error("Low Match ❌")
    st.markdown('</div>', unsafe_allow_html=True)

    # Back
    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()
