import streamlit as st
import pdfplumber
import docx2txt
import re
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# -------------------------------
# THEME
# -------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #d1fae5);
}
body, p, span, div, label {
    color: #1f2937 !important;
}
h1, h2, h3 {
    color: #111827 !important;
}
.glass {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
}
.stButton>button {
    background: linear-gradient(to right, #4f46e5, #22c55e);
    color: white;
    border-radius: 12px;
}
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, #1e293b, #334155);
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
# HOME
# -------------------------------
if st.session_state.page == "home":

    st.title("💎 AI Resume Screening System")
    st.subheader("🚀 Smart AI-powered Resume Analyzer")

    st.markdown("""
    <div class="glass">
    📌 Upload resume<br>
    📌 Paste job description<br>
    📌 Get ATS score<br>
    📌 Improve instantly
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf","docx"])
    job_description = st.text_area("📝 Enter Job Description")

    if st.button("🔍 Analyze Resume"):
        if uploaded_file and job_description:
            text = extract_text(uploaded_file)
            st.session_state.data = {"text": text, "jd": job_description}
            st.session_state.page = "analysis"
            st.rerun()
        else:
            st.warning("⚠️ Please upload resume and enter job description")

# -------------------------------
# ANALYSIS
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

    # 🎯 ATS Circular Score
    st.subheader("🎯 ATS Score")
    fig, ax = plt.subplots()
    ax.pie([final_score, 1-final_score], labels=["Match", ""], autopct='%1.0f%%')
    ax.set_title("ATS Match Score")
    st.pyplot(fig)

    # 📌 Info
    st.subheader("📌 Extracted Info")
    st.write("Email:", email)
    st.write("Phone:", phone)
    st.write("Skills:", skills)

    # 📊 Skill Chart
    st.subheader("📊 Skills Match Chart")
    skill_values = [1 if skill in skills else 0 for skill in skills_db]

    fig2, ax2 = plt.subplots()
    ax2.bar(skills_db, skill_values)
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # 🎯 Decision
    st.subheader("🎯 Result")
    if final_score > 0.7:
        st.success("Excellent Match 🎉")
    elif final_score > 0.5:
        st.warning("Moderate Match ⚠️")
    else:
        st.error("Low Match ❌")

    # 🤖 Smart Suggestions
    st.subheader("🤖 Suggestions")

    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.write("🔧 Improve these skills:", missing_skills)

    if similarity < 0.5:
        st.write("📄 Your resume content is not aligned with job description. Add relevant keywords.")

    if not email:
        st.write("📧 Add professional email")

    if not phone:
        st.write("📱 Add phone number")

    if final_score > 0.7:
        st.success("Your resume is strong 💪")

    # Back
    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()
