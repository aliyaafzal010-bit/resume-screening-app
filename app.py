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
# MODERN UI CSS 🔥
# -------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #dbeafe, #dcfce7);
    font-family: 'Segoe UI', sans-serif;
}

/* Center container */
.main-container {
    max-width: 800px;
    margin: auto;
    padding-top: 30px;
}

/* Card UI */
.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Input fields fix */
input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 8px !important;
}

/* File uploader fix */
[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    padding: 15px;
    border-radius: 10px;
}

/* Text area fix */
[data-testid="stTextArea"] textarea {
    background-color: white !important;
    color: black !important;
}

/* Button */
.stButton>button {
    width: 100%;
    background: linear-gradient(to right, #2563eb, #22c55e);
    color: white;
    border-radius: 10px;
    padding: 12px;
    font-size: 16px;
    font-weight: bold;
    border: none;
}

/* Title */
.title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #1e293b;
}

.subtitle {
    text-align: center;
    color: #475569;
    margin-bottom: 20px;
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

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>💎 AI Resume Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Smart AI-powered Resume Screening System</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf","docx"])
    job_description = st.text_area("📝 Paste Job Description")

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

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# ANALYSIS PAGE
# -------------------------------
elif st.session_state.page == "analysis":

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>📊 Resume Analysis</div>", unsafe_allow_html=True)

    text = st.session_state.data["text"]
    jd = st.session_state.data["jd"]

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    similarity = calculate_similarity(text, jd)

    jd_skills = extract_skills(jd)
    skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)

    final_score = (0.7 * similarity) + (0.3 * skill_score)

    # Info
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("📧 Email:", email)
    st.write("📱 Phone:", phone)
    st.write("🧠 Skills:", skills)
    st.markdown("</div>", unsafe_allow_html=True)

    # Scores
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("📊 Similarity Score:", round(similarity,2))
    st.write("🧩 Skill Match:", round(skill_score,2))
    st.write("⭐ Final Score:", round(final_score,2))
    st.progress(float(final_score))
    st.markdown("</div>", unsafe_allow_html=True)

    # Decision
    if final_score > 0.7:
        st.success("✅ Excellent Match")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match")
    else:
        st.error("❌ Poor Match")

    # Suggestions
    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("🔧 Missing Skills:", ", ".join(missing_skills))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("🎉 Your resume matches well!")

    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
