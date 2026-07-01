# 📚 StudyHelper AI

Aplikasi **Streamlit** berbasis **RAG (Retrieval-Augmented Generation)** yang membantu mahasiswa belajar dengan cara meringkas materi, menjawab pertanyaan, dan membuat kuis dari **file PDF atau video YouTube**. Ditenagai oleh **LangChain**, **FAISS**, dan **Google Gemini**.

![python](https://img.shields.io/badge/Python-3.x-blue)
![streamlit](https://img.shields.io/badge/Streamlit-app-red)
![langchain](https://img.shields.io/badge/LangChain-RAG-green)
![gemini](https://img.shields.io/badge/Google-Gemini-orange)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

## 📌 Overview

StudyHelper AI mengubah materi belajar (PDF atau transkrip YouTube) menjadi asisten belajar interaktif. Pengguna cukup mengunggah dokumen atau menempelkan link video, lalu aplikasi akan mengekstrak isinya, membangun basis pengetahuan, dan memungkinkan pengguna meringkas, bertanya jawab, serta menghasilkan kuis dari materi tersebut.

## ✨ Features

- **Ringkasan materi otomatis:** Merangkum isi PDF atau video menjadi ringkasan terstruktur dalam Bahasa Indonesia.
- **Chatbot tanya jawab (Q&A):** Bertanya jawab dengan materi menggunakan pendekatan RAG, sehingga jawaban berbasis konteks dokumen dan tidak mengarang.
- **Generator kuis pilihan ganda:** Membuat soal latihan dari materi untuk menguji pemahaman.

## 🧠 How It Works (RAG Pipeline)

1. **Ekstraksi teks:** Membaca teks dari PDF (`PyPDF2`) atau transkrip YouTube (`YoutubeLoader`).
2. **Chunking:** Memecah teks panjang menjadi potongan dengan `CharacterTextSplitter` (chunk 1000, overlap 200).
3. **Embedding & indexing:** Mengubah potongan teks menjadi vektor (`HuggingFace instructor-xl`) lalu menyimpannya di **FAISS** vector store.
4. **Retrieval & generation:** Mengambil konteks relevan dari FAISS, lalu **Google Gemini** menghasilkan jawaban atau ringkasan berdasarkan konteks tersebut.

## 🧰 Tech Stack

- **Framework:** Streamlit (multipage app)
- **LLM:** Google Gemini via `langchain-google-genai`
- **Orkestrasi RAG:** LangChain, `langchain-community`
- **Vector store & embeddings:** FAISS (`faiss-cpu`), `sentence-transformers`
- **Ekstraksi dokumen:** PyPDF2, YoutubeLoader
- **Utilitas:** python-dotenv

## ▶️ How to Run (Local)

1. **Clone repositori**
   ```bash
   git clone https://github.com/Ishalllll/ai-study-helper.git
   cd ai-study-helper
   ```
2. **Install dependency**
   ```bash
   pip install -r requirements.txt
   ```
3. **Siapkan environment variable.** Buat file `.env` di root berisi:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key
   MODEL_NAME=gemini-2.0-flash-lite
   ```
   (`MODEL_NAME` opsional, default `gemini-2.0-flash-lite`.)
4. **Jalankan aplikasi**
   ```bash
   streamlit run Chatbot.py
   ```

> Catatan: pada run pertama, model embedding (`instructor-xl`) akan diunduh dan berukuran cukup besar, jadi proses awal mungkin memakan waktu.

## 📝 Notes & Limitations

Fitur transkrip YouTube mungkin tidak berfungsi pada versi online (cloud) karena pembatasan dari pihak YouTube terhadap server cloud. Fitur ini berjalan lancar saat aplikasi dijalankan secara lokal.

## 👤 Author

**Muhammad Faishal Ardiansyah**, [@Ishalllll](https://github.com/Ishalllll)
