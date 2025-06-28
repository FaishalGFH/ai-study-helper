import streamlit as st
import google.generativeai as genai
import os
import json

def generate_quiz(text,num):
    st.set_page_config(page_title="Quiz Generator", page_icon="📄")
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_model = os.getenv("MODEL_NAME","gemini-2.0-flash-lite")
        if not gemini_api_key:
            return "Gemini API not found"
        
        json_schema = {
            "type":"array",
            "items":{
                "type": "object",
                "properties":{
                    "question":{"type":"string"},
                    "options":{
                        "type":"array",
                        "items":{"type":"string"}
                    },
                    "correct_answer":{"type":"string"}
                },
                "required":["question","options","correct_answer"]
            }
        }
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(
            gemini_model,
            generation_config={
                "response_mime_type":"application/json",
                "response_schema":json_schema
            }
        )

        quiz_template = f"""
        Kamu adalah seorang guru yang ahli dalam membuat kuis.
        Berdasarkan materi berikut, buat kuis pilihan ganda sebanyak {num} dengan menggunakan bahasa indonesia.
        Setiap pertanyaan memiliki 4 pilihan jawaban, dimana salah satu jawaban harus benar dan 3 lainnya adalah pengecoh yang masuk akal.
        Pastikan bahwa jawaban yang benar ada di dalam daftar pilihan jawaban.

        Teks materi:
        ---
        {text}
        ---
        """

        response = model.generate_content(quiz_template)
        return json.loads(response.text)

    except Exception as e:
        st.error(f"There is an error, please reload the app: {e}")


st.title("it's time to recalling your understanding🧠")

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = {}

raw_text = st.session_state.get("raw_text","")
if not raw_text:
    st.error("Material not found, please realod the app.")
    st.stop()

word_count = len(raw_text.split())
num_questions = max(3,min(10,word_count // 200))

# Buat quiz
if st.button("Generate new quiz",type="primary"):
    # Untuk reset quiz
    st.session_state.quiz_data = None
    st.session_state.quiz_submitted = False
    st.session_state.user_answer = {}

    with st.spinner("Formulating questions..."):
        quiz_data = generate_quiz(raw_text,num_questions)
        if quiz_data:
            st.session_state.quiz_data = quiz_data
        else:
            st.error("Failed to create quuestions, try again!")

if st.session_state.quiz_data:
    st.subheader("Please answer the questions below")

    with st.form("form kuis"):
        for i, q in enumerate(st.session_state.quiz_data):
            st.subheader(f"{i+1}. {q['question']}")
            st.session_state.user_answer[i] = st.radio(
                "Choose your answer:",
                options=q["options"],
                key=f"q_{i}",
                index=None    
            )
            st.divider()
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state.quiz_submitted = True
            st.rerun()

if st.session_state.quiz_submitted and st.session_state.quiz_data:
    st.divider()
    st.header("📃 Your results")

    score = 0
    quiz_data = st.session_state.quiz_data
    user_answers = st.session_state.user_answer

    for i, q in enumerate(quiz_data):
        user_answer = user_answers.get(i)
        correct_answer = q['correct_answer']

        if user_answer == correct_answer:
            score += 1
            with st.container(border=True):
                st.success(f"Pertanyaan {i+1}: Benar!",icon="✅")
                st.markdown(f"**Pertanyaan:** {q['question']}")
                st.markdown(f"**Jawaban anda:** {user_answer}")
        
        else:
            with st.container(border=True):
                st.error(f"Pertanyaan {i+1}: salah!",icon="❌")
                st.markdown(f"**Pertanyaan:** {q['question']}")
                st.markdown(f"**Jawaban anda:** {user_answer}")
                st.markdown(f"**Jawaban yang benar:** {correct_answer}")

    final_score = (score/len(quiz_data))*100 if len(quiz_data)>0 else 0
    st.divider()
    st.subheader(f"Your score: {final_score:.2f}")
    if final_score >= 70:
        st.balloons()
        st.success(f"Selamat, pemahaman anda sudah baik!")
    else:
        st.warning(f"Perlu sedikit belajar lagi, yuk! Coba lagi nanti.")

