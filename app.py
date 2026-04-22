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
# COLORFUL UI CSS (FIXED)
# -------------------------------
st.markdown("""
<style>

/* Background Gradient */
.stApp {
    background: linear-gradient(to right, #dbeafe, #dcfce7);
}

/* Text Fix */
body, p, div {
    color: black !important;
}

/* Card Style */
.card {
    background: #ffffff;
    color: black !important;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 10px;
    font-size: 16px;
}

/* Headings */
h1, h2, h3 {
    color: #1e293b !important;
}

/* Button */
.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
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
    st.markdown("### ✨ Smart Resume Analyzer using AI")

    st.write("""
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
    # OUTPUT
    # -------------------------------
    st.subheader("📌 Extracted Information")

    st.markdown(f"<div class='card'>📧 Email: {email}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>📱 Phone: {phone}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>🧠 Skills: {skills}</div>", unsafe_allow_html=True)

    st.subheader("📈 Analysis Scores")

    st.markdown(f"<div class='card'>📊 Similarity Score: {round(similarity,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>🧩 Skill Match: {round(skill_score,2)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>⭐ Final Score: {round(final_score,2)}</div>", unsafe_allow_html=True)

    # Progress Bar
    st.progress(float(final_score))

    # -------------------------------
    # FINAL DECISION
    # -------------------------------
    st.subheader("🎯 Final Decision")

    if final_score > 0.7:
        st.success("✅ Excellent Match - Highly Suitable Candidate")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match - Needs Improvement")
    else:
        st.error("❌ Poor Match - Improve Skills")

    # -------------------------------
    # SUGGESTIONS
    # -------------------------------
    st.subheader("💡 Improvement Suggestions")

    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.write("🔧 Add these skills:")
        st.write(missing_skills)
    else:
        st.success("🎉 Your resume matches well!")

    # Back button
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()
 
