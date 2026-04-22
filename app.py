import streamlit as st
import PyPDF2
import re
import pandas as pd

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------------------------
# TITLE
# ---------------------------
st.title("📄 AI Resume Analyzer")
st.markdown("Upload your resume and get ATS score, skill match, and suggestions.")

# ---------------------------
# FILE UPLOAD
# ---------------------------
uploaded_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])

# ---------------------------
# JOB DESCRIPTION
# ---------------------------
jd = st.text_area("Paste Job Description here")

# ---------------------------
# SAMPLE SKILLS LIST
# ---------------------------
skills_list = [
    "python", "java", "c++", "html", "css", "javascript",
    "sql", "machine learning", "data analysis", "react",
    "node.js", "mongodb", "git", "excel"
]

# ---------------------------
# FUNCTION: EXTRACT TEXT
# ---------------------------
def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

# ---------------------------
# FUNCTION: EXTRACT EMAIL
# ---------------------------
def extract_email(text):
    match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", text)
    return match[0] if match else "Not Found"

# ---------------------------
# FUNCTION: EXTRACT SKILLS
# ---------------------------
def extract_skills(text):
    found_skills = []
    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)
    return found_skills

# ---------------------------
# MAIN LOGIC
# ---------------------------
if uploaded_file is not None:

    text = extract_text(uploaded_file)

    st.subheader("📊 Extracted Information")

    col1, col2 = st.columns(2)

    with col1:
        email = extract_email(text)
        st.write(f"📧 Email: {email}")

    with col2:
        skills = extract_skills(text)
        st.write(f"🛠 Skills: {', '.join(skills) if skills else 'None'}")

    # ---------------------------
    # MATCHING WITH JD
    # ---------------------------
    if jd:
        jd = jd.lower()

        matched = []
        missing = []

        for skill in skills_list:
            if skill in jd and skill in skills:
                matched.append(skill)
            elif skill in jd and skill not in skills:
                missing.append(skill)

        # SCORE CALCULATION
        if len(jd) > 0:
            score = int((len(matched) / (len(matched) + len(missing) + 1)) * 100)
        else:
            score = 0

        st.subheader("📈 ATS Score")
        st.progress(score)
        st.write(f"### {score}% Match")

        # ---------------------------
        # SKILL DISPLAY
        # ---------------------------
        st.subheader("✅ Matched Skills")
        st.write(matched if matched else "No matches")

        st.subheader("❌ Missing Skills")
        st.write(missing if missing else "None")

        # ---------------------------
        # GRAPH
        # ---------------------------
        st.subheader("📊 Skill Match Graph")

        data = pd.DataFrame({
            "Category": ["Matched", "Missing"],
            "Count": [len(matched), len(missing)]
        })

        st.bar_chart(data.set_index("Category"))

        # ---------------------------
        # SUGGESTIONS
        # ---------------------------
        st.subheader("💡 Suggestions")

        if score < 40:
            st.error("Your resume needs improvement. Add relevant skills and keywords.")
        elif score < 70:
            st.warning("Good resume, but can be improved by adding missing skills.")
        else:
            st.success("Great! Your resume is well optimized.")

        if missing:
            st.write("👉 Try adding these skills:", ", ".join(missing))

    else:
        st.info("Paste a Job Description to get ATS score.")
