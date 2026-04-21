import streamlit as st
import pdfplumber
import docx2txt
import re
import spacy
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# spaCy MODEL LOAD (FIXED FOR CLOUD)
# -------------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# -------------------------------
# Extract Text
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


# -------------------------------
# Extract Email & Phone
# -------------------------------
def extract_email(text):
    return re.findall(r'\S+@\S+', text)

def extract_phone(text):
    return re.findall(r'\d{10}', text)


# -------------------------------
# Extract Skills
# -------------------------------
skills_db = [
    "python","java","sql","machine learning","ai",
    "data science","deep learning","html","css","javascript"
]

def extract_skills(text):
    text = text.lower()
    return [skill for skill in skills_db if skill in text]


# -------------------------------
# Similarity Calculation
# -------------------------------
def calculate_similarity(resume, jd):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume, jd])
    score = cosine_similarity(vectors[0:1], vectors[1:2])
    return score[0][0]


# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="AI Resume Screener", layout="centered")

st.title("📄 AI Resume Screening System")
st.write("Upload your resume and compare with job description")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
job_description = st.text_area("Enter Job Description")

if st.button("Analyze Resume"):
    
    if uploaded_file is not None and job_description.strip() != "":
        
        text = extract_text(uploaded_file)
        
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)
        
        similarity = calculate_similarity(text, job_description)
        
        jd_skills = extract_skills(job_description)
        skill_score = len(set(skills) & set(jd_skills)) / max(len(jd_skills), 1)
        
        final_score = (0.7 * similarity) + (0.3 * skill_score)
        
        st.subheader("🔍 Results")
        
        st.write("📧 Email:", email)
        st.write("📱 Phone:", phone)
        st.write("🧠 Skills:", skills)
        
        st.write("📊 Similarity Score:", round(similarity, 2))
        st.write("🧩 Skill Match Score:", round(skill_score, 2))
        st.write("⭐ Final Score:", round(final_score, 2))
        
        if final_score > 0.6:
            st.success("✅ Strong Candidate")
        else:
            st.error("❌ Not a Good Match")
    
    else:
        st.warning("⚠️ Please upload resume and enter job description")
