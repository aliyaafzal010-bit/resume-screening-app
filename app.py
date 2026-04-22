import streamlit as st
import pdfplumber
import docx2txt
import re
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# -------------------------------
# 🔥 PREMIUM GLASS UI
# -------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #667eea, #764ba2);
}

/* Glass Card */
.glass {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    border-radius: 18px;
    padding: 20px;
    color: white;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* Text */
h1,h2,h3,label,p {
    color: white !important;
}

/* Inputs */
input, textarea {
    background-color: rgba(255,255,255,0.9) !important;
    color: black !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(0,0,0,0.5);
    border-radius: 12px;
    padding: 10px;
}
[data-testid="stFileUploader"] * {
    color: white !important;
}

/* Button */
.stButton>button {
    background: linear-gradient(to right, #ff7e5f, #feb47b);
    color: white;
    border-radius: 12px;
}

/* Progress */
.stProgress > div > div > div {
    background: #ff7e5f;
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

skills_db = ["python","java","sql","machine learning","ai","data science","deep learning","html","css","javascript"]

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

    st.title("💎 AI Resume Analyzer")
    st.markdown('<div class="glass">Upload resume and get ATS score instantly 🚀</div>', unsafe_allow_html=True)

    file = st.file_uploader("Upload Resume", type=["pdf","docx"])
    jd = st.text_area("Paste Job Description")

    if st.button("Analyze"):
        if file and jd:
            text = extract_text(file)
            st.session_state.data = {"text": text, "jd": jd}
            st.session_state.page = "analysis"
            st.rerun()

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
    final_score = (0.7 * similarity) + (0.3 * skill_score)

    st.title("📊 Dashboard")

    # 🔥 Layout
    col1, col2 = st.columns([1,1])

    # 🎯 Circular Score (SMALL)
    with col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(3,3))  # 👈 FIXED SIZE
        ax.pie([final_score, 1-final_score], labels=["",""], autopct='%1.0f%%')
        ax.set_title("ATS Score")
        st.pyplot(fig)

        st.markdown('</div>', unsafe_allow_html=True)

    # 📊 Skill Chart (SMALL)
    with col2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)

        values = [1 if s in skills else 0 for s in skills_db]

        fig2, ax2 = plt.subplots(figsize=(4,3))  # 👈 FIXED SIZE
        ax2.bar(skills_db, values)
        plt.xticks(rotation=45, fontsize=8)
        st.pyplot(fig2)

        st.markdown('</div>', unsafe_allow_html=True)

    # 📌 Info
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Extracted Skills")
    st.write(skills)
    st.markdown('</div>', unsafe_allow_html=True)

    # 🎯 Result
    st.markdown('<div class="glass">', unsafe_allow_html=True)
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
