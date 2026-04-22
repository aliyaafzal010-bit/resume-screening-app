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
# ADVANCED UI CSS + ANIMATION
# -------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #dbeafe, #dcfce7);
}

/* Fade animation */
.fade-in {
    animation: fadeIn 1.2s ease-in;
}
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

/* Glass Card */
.glass {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    margin-top: 10px;
}

/* Inputs */
input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 8px !important;
}

/* Button */
.stButton>button {
    background: linear-gradient(to right, #22c55e, #3b82f6);
    color: white;
    padding: 10px 25px;
    border-radius: 10px;
    font-weight: bold;
    border: none;
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

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("""
        <div class="fade-in">
        <h1 style='font-size:48px;'>Build a Better Resume 🚀</h1>
        <p style='font-size:18px; color:#374151;'>
        Upload your resume and compare it with job descriptions using AI.
        Get instant feedback, match score, and improvement suggestions.
        </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass fade-in">
        📌 AI-based Resume Analysis<br>
        📌 Skill Matching & Score<br>
        📌 Improvement Suggestions
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass fade-in">
        <h3>📊 Sample Score</h3>
        <h1 style="color:#22c55e;">82%</h1>
        ✔ Good Skills Match <br>
        ✔ Strong Keywords <br>
        ❗ Improve Formatting
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📤 Upload Your Resume")

    uploaded_file = st.file_uploader("", type=["pdf","docx"])
    job_description = st.text_area("📝 Paste Job Description")

    if st.button("🚀 Analyze Now"):
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

    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

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
    st.markdown(f"<div class='glass'>📧 {email}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass'>📱 {phone}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='glass'>🧠 {skills}</div>", unsafe_allow_html=True)

    # Graph
    st.subheader("📊 Score Visualization")

    labels = ['Similarity', 'Skill Match', 'Final']
    values = [similarity, skill_score, final_score]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    st.pyplot(fig)

    # Progress
    st.subheader("📈 Overall Score")
    st.progress(float(final_score))

    # Decision
    st.subheader("🎯 Final Decision")
    if final_score > 0.7:
        st.success("✅ Excellent Match")
    elif final_score > 0.5:
        st.warning("⚠️ Moderate Match")
    else:
        st.error("❌ Needs Improvement")

    # Suggestions
    st.subheader("💡 Suggestions")
    missing_skills = list(set(jd_skills) - set(skills))

    if missing_skills:
        st.markdown(
            "<div class='glass'><b>Missing Skills:</b><br>" + ", ".join(missing_skills) + "</div>",
            unsafe_allow_html=True
        )
    else:
        st.success("🎉 Great Match!")

    if st.button("⬅️ Back"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
 
