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
# GLASS UI CSS (UNCHANGED)
# -------------------------------
st.markdown("""<style>
.stApp {background: linear-gradient(135deg, #eef2ff, #d1fae5);}
body, p, span, div, label {color: #1f2937 !important;}
.glass {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}
input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #1e293b, #334155);
    border-radius: 12px;
    padding: 12px;
}
[data-testid="stFileUploader"] * {color: white !important;}
.stButton>button {
    background: linear-gradient(to right, #4f46e5, #22c55e);
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
}
.stProgress > div > div > div {
    background: linear-gradient(to right, #4f46e5, #22c55e);
}
</style>""", unsafe_allow_html=True)

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

# 🔥 IMPROVED SKILLS DB (LIGHTWEIGHT)
skills_db = [
    "python","java","sql","machine learning","ai","data science",
    "deep learning","html","css","javascript","react","nodejs",
    "mongodb","flask","django","pandas","numpy","excel"
]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_db if skill in text]

# 🔥 LIGHTWEIGHT SIMILARITY (SAFE)
def calculate_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume, jd])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

# 🔥 NEW STRUCTURED EXTRACTION
def extract_name(text):
    lines = text.strip().split("\n")
    return lines[0] if lines else "Not Found"

def extract_education(text):
    keywords = ["btech", "bachelor", "degree", "university", "college"]
    return [line for line in text.split("\n") if any(k in line.lower() for k in keywords)]

def extract_experience(text):
    keywords = ["intern", "experience", "worked"]
    return [line for line in text.split("\n") if any(k in line.lower() for k in keywords)]

# SECTION CHECK
def check_sections(text):
    text = text.lower()
    sections = {
        "Education": ["education", "degree", "university", "college"],
        "Projects": ["project"],
        "Experience": ["experience", "internship", "work"]
    }
    missing = []
    for section, keywords in sections.items():
        if not any(keyword in text for keyword in keywords):
            missing.append(section)
    return missing

# -------------------------------
# SESSION STATE
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------------------
# HOME PAGE
# -------------------------------
if st.session_state.page == "home":

    st.markdown("<h1 style='text-align:center;font-size: 52px;'>📊 AI Resume Parser</h1>", unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align: center;font-size: 22px;color: #374151;'>
    " 🚀 Smart AI-powered Resume Screening System "
    </p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass">
    📌 Upload your resume<br>
    📌 Paste job description<br>
    📌 Get AI-based analysis & score<br>
    📌 Improve your resume easily
    </div>
    """, unsafe_allow_html=True)

    # 🔥 MULTIPLE FILE SUPPORT (HR FEATURE)
    uploaded_files = st.file_uploader("📄 Upload Resume(s)", type=["pdf","docx"], accept_multiple_files=True)
    job_description = st.text_area("📝 Enter Job Description")

    if st.button("🔍 Analyze Resume"):
        if uploaded_files and job_description:
            results = []

            for file in uploaded_files:
                text = extract_text(file)
                score = calculate_similarity(text, job_description)
                results.append((file.name, text, score))

            # 🔥 RANKING
            results.sort(key=lambda x: x[2], reverse=True)

            st.session_state.results = results
            st.session_state.jd = job_description
            st.session_state.page = "analysis"
            st.rerun()
        else:
            st.warning("⚠️ Please upload resume and enter job description")

# -------------------------------
# ANALYSIS PAGE
# -------------------------------
elif st.session_state.page == "analysis":

    st.title("📊 Resume Analysis Dashboard")

    results = st.session_state.results
    jd = st.session_state.jd

    # 🔥 RANKING DISPLAY
    st.markdown("### 🏆 Candidate Ranking")
    for i, (name, _, score) in enumerate(results):
        st.markdown(f"<div class='glass'>#{i+1} {name} → {round(score,2)}</div>", unsafe_allow_html=True)

    # TOP RESUME
    text = results[0][1]

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    name = extract_name(text)
    education = extract_education(text)
    experience = extract_experience(text)

    similarity = results[0][2]
    jd_skills = extract_skills(jd)

    skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills),1)
    final_score = (0.7 * similarity) + (0.3 * skill_score)

    missing_sections = check_sections(text)

    # STRUCTURED INFO
    st.markdown("### 📌 Extracted Information")
    st.markdown(f"""
    <div class='glass'>
    👤 <b>Name:</b> {name}<br><br>
    📧 <b>Email:</b> {email}<br><br>
    📱 <b>Phone:</b> {phone}<br><br>
    🧠 <b>Skills:</b> {skills}<br><br>
    🎓 <b>Education:</b> {education}<br><br>
    💼 <b>Experience:</b> {experience}
    </div>
    """, unsafe_allow_html=True)

    # SCORES
    st.markdown("### 📈 Analysis Scores")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class='glass'>📊 Similarity<br><h3>{round(similarity,2)}</h3></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='glass'>🧩 Skill Match<br><h3>{round(skill_score,2)}</h3></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<div class='glass'>⭐ Final Score<br><h3>{round(final_score,2)}</h3></div>", unsafe_allow_html=True)

    st.progress(float(final_score))

    # DECISION
    st.markdown("### 🎯 Final Decision")

    if final_score > 0.7:
        st.success("✅ Excellent Match - Highly Suitable Candidate")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match - Needs Improvement")
    else:
        st.error("❌ Poor Match - Improve Skills")

    # SUGGESTIONS
    st.markdown("### 💡 Suggestions")

    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.markdown(f"<div class='glass'>🔧 Improve these skills: {missing_skills}</div>", unsafe_allow_html=True)

    if similarity < 0.5:
        st.markdown("<div class='glass'>📄 Add more relevant keywords from job description</div>", unsafe_allow_html=True)

    if not email:
        st.markdown("<div class='glass'>📧 Add professional email</div>", unsafe_allow_html=True)

    if not phone:
        st.markdown("<div class='glass'>📱 Add phone number</div>", unsafe_allow_html=True)

    # SECTION CHECK
    st.markdown("### 📄 Resume Section Check")

    if missing_sections:
        st.markdown(f"<div class='glass'>⚠️ Missing Sections: {missing_sections}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass'>✅ All important sections are present</div>", unsafe_allow_html=True)

    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"
        st.rerun()



