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
# CSS (UNCHANGED)
# -------------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #eef2ff, #d1fae5); }

.glass {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FUNCTIONS (UNCHANGED)
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

skills_db = ["python","java","sql","machine learning","ai",
             "data science","deep learning","html","css","javascript"]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_db if skill in text]

def calculate_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume, jd])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

# -------------------------------
# NEW SAFE FUNCTIONS
# -------------------------------

def check_sections(text):
    text = text.lower()
    sections = {
        "Education": ["education", "degree", "college"],
        "Projects": ["project"],
        "Experience": ["experience", "internship"]
    }
    missing = []
    for sec, keys in sections.items():
        if not any(k in text for k in keys):
            missing.append(sec)
    return missing

def extract_education(text):
    text = text.lower()
    if "btech" in text or "b.e" in text:
        return "Bachelor's Degree"
    elif "mba" in text:
        return "MBA"
    return "Not Found"

def extract_experience(text):
    matches = re.findall(r'(\d+)\s+years', text.lower())
    return matches if matches else ["Not Found"]

# -------------------------------
# SESSION
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------------------
# HOME
# -------------------------------
if st.session_state.page == "home":

    st.markdown("""
    <h1 style='text-align:center;font-size:48px;
    background: linear-gradient(to right,#4f46e5,#22c55e);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;'>
    📊 AI Resume Analyzer
    </h1>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Upload Resume(s)", type=["pdf","docx"], accept_multiple_files=True)
    job_description = st.text_area("Enter Job Description")

    if st.button("Analyze"):
        if uploaded_files and job_description:
            results = []

            for file in uploaded_files:
                text = extract_text(file)
                similarity = calculate_similarity(text, job_description)
                skills = extract_skills(text)
                jd_skills = extract_skills(job_description)

                skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)
                final_score = (0.7 * similarity) + (0.3 * skill_score)

                results.append({
                    "name": file.name,
                    "text": text,
                    "score": final_score,
                    "skills": skills
                })

            # SORT (Ranking)
            results = sorted(results, key=lambda x: x["score"], reverse=True)

            st.session_state.results = results
            st.session_state.jd = job_description
            st.session_state.page = "analysis"
            st.rerun()

# -------------------------------
# ANALYSIS
# -------------------------------
elif st.session_state.page == "analysis":

    st.title("📊 Resume Analysis Dashboard")

    results = st.session_state.results
    jd = st.session_state.jd

    # 🔥 Ranking Display
    st.markdown("### 🏆 Candidate Ranking")
    for i, r in enumerate(results):
        st.markdown(f"<div class='glass'>#{i+1} {r['name']} → Score: {round(r['score'],2)}</div>", unsafe_allow_html=True)

    # 🔹 Detailed View (Top Candidate)
    top = results[0]
    text = top["text"]

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    missing_sections = check_sections(text)

    # NEW EXTRACTIONS
    education = extract_education(text)
    experience = extract_experience(text)

    # 🔥 STRUCTURED OUTPUT (HR READY)
    st.markdown("### 📂 Structured Resume Data")
    st.json({
        "Name": top["name"],
        "Email": email,
        "Phone": phone,
        "Skills": skills,
        "Education": education,
        "Experience": experience,
        "Missing Sections": missing_sections
    })

    # Existing UI continues (SAFE)
    st.markdown("### 📌 Extracted Info")
    st.markdown(f"<div class='glass'>Email: {email}<br>Phone: {phone}<br>Skills: {skills}</div>", unsafe_allow_html=True)

    st.markdown("### 📄 Section Check")
    if missing_sections:
        st.markdown(f"<div class='glass'>Missing: {missing_sections}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass'>All sections present</div>", unsafe_allow_html=True)

    # Back
    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()


