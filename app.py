import streamlit as st
import pdfplumber
import docx2txt
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Resume Checker", layout="wide")

# -------------------------------
# MODERN LANDING UI
# -------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #dbeafe, #e0f2fe, #dcfce7);
}

/* Main container */
.block-container {
    padding-top: 2rem;
}

/* Title */
.title {
    font-size: 50px;
    font-weight: 700;
    color: #1e293b;
}

/* Subtitle */
.subtitle {
    font-size: 18px;
    color: #475569;
}

/* Upload Card */
.upload-box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    border: 2px dashed #22c55e;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* Input fix */
input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 8px !important;
}

/* Button */
.stButton>button {
    background: linear-gradient(to right, #22c55e, #2563eb);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
}

/* Cards */
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 10px;
    color: black;
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
# SESSION
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------------------
# HOME PAGE (LIKE IMAGE 🔥)
# -------------------------------
if st.session_state.page == "home":

    col1, col2 = st.columns([1.2, 1])

    # LEFT SIDE TEXT
    with col1:
        st.markdown("<div class='title'>Is your resume good enough?</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='subtitle'>
        A smart AI resume checker that analyzes your resume and matches it with job descriptions.
        Get instant feedback and improve your chances of selection.
        </div>
        """, unsafe_allow_html=True)

    # RIGHT SIDE UPLOAD BOX
    with col2:
        st.markdown("<div class='upload-box'>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf","docx"])
        job_description = st.text_area("📝 Paste Job Description")

        if st.button("🚀 Check Resume"):
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

    # INFO
    st.subheader("📌 Extracted Information")
    st.markdown(f"<div class='card'>📧 Email: {email}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>📱 Phone: {phone}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>🧠 Skills: {skills}</div>", unsafe_allow_html=True)

    # SCORES
    st.subheader("📈 Scores")
    st.markdown(f"<div class='card'>📊 Similarity: {round(similarity,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>🧩 Skill Match: {round(skill_score,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>⭐ Final Score: {round(final_score,2)}</div>", unsafe_allow_html=True)

    st.progress(float(final_score))

    # RESULT
    st.subheader("🎯 Final Decision")
    if final_score > 0.7:
        st.success("✅ Excellent Match")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match")
    else:
        st.error("❌ Poor Match")

    # SUGGESTIONS
    st.subheader("💡 Suggestions")
    missing = list(set(jd_skills) - set(skills))

    if missing:
        st.markdown(f"<div class='card'>Add these skills: {', '.join(missing)}</div>", unsafe_allow_html=True)
    else:
        st.success("🎉 Your resume is strong!")

    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()
 
