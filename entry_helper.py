import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import YoutubeLoader
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate


def get_pdf_text(pdf_local):
    text = ""
    if pdf_local:
        for pdf in pdf_local:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text+= page.extract_text()
    return text

def get_yt_text(url):
    try:
        loader = YoutubeLoader.from_youtube_url(
            url, 
            add_video_info=False,
            language=['id', 'en']
        )
        documents = loader.load()
        return " ".join([doc.page_content for doc in documents])
    except Exception as e:
        st.error(f"Gagal memuat transkrip dari YouTube: {e}")
        return None

def get_text_chunks(text):
    if not text:
        return []
    text_splitter = CharacterTextSplitter(
        separator= "\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len
    )
    chunks_ = text_splitter.split_text(text)
    return chunks_

def get_vectorDB(text_chunks):
    if not text_chunks:
        return None
    # embeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceEmbeddings(
        model_name = "hkunlp/instructor-xl",
        model_kwargs = {'device': 'cpu'}
    )
    vectorStore = FAISS.from_texts(
        texts = text_chunks,
        embedding = embeddings
    )
    return vectorStore

def get_conversation_chain(vectorDB):
    if not vectorDB:
        return None
    # llm = ChatOpenAI()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("MODEL_NAME","gemini-2.0-flash-lite")

    template = """
    Anda adalah asisten AI yang ramah. Jawab pertanyaan hanya berdasarkan konteks yang diberikan.
    Jika Anda tidak menemukan jawaban di dalam konteks, katakan dengan sopan bahwa informasi tersebut tidak ada dalam dokumen. Jangan mengarang jawaban.

    Konteks: {context}
    Pertanyaan: {question}
    """
    QA_Prompt = PromptTemplate(
        template=template,
        input_variables=["context","question"]
    )

    llm = ChatGoogleGenerativeAI(
        model = gemini_model,
        google_api_key = gemini_api_key
    )
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True,
        output_key="answer"
    )
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever = vectorDB.as_retriever(),
        memory = memory,
        return_source_documents = True,
        combine_docs_chain_kwargs = {"prompt":QA_Prompt}
    )
    return conversation_chain

def generate_summary(text: str):
    try: 
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_model = os.getenv("MODEL_NAME","gemini-2.0-flash-lite")
        if not gemini_api_key:
            return "Gemini API Key tidak ditemukan"
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(gemini_model)

        user_query = (
            '''Anda adalah seorang asisten AI yang ahli dalam meringkas materi.
            Berikut adalah teks dari dokumen atau video yang diunggah oleh pengguna. 
            Tugas Anda adalah membuat ringkasan yang jelas dan informatif dalam Bahasa Indonesia.
            Jika pertanyaan tidak dapat dijawab menggunakan konteks yang ada, katakan dengan sopan bahwa informasinya tidak ditemukan dalam dokumen. 
            Jangan mencoba mengarang jawaban.
            "Contoh jawaban jika tidak tahu:"
            - Maaf, informasi mengenai hal tersebut tidak ada dalam materi yang Anda berikan.
            - "Berdasarkan dokumen ini, saya tidak menemukan pembahasan tentang itu. Apakah ada hal lain yang bisa saya bantu?'''
            "Sajikan penjelasan dalam format paragraf, dimana 1 paragraf memuat 1 pembahasan untuk memudahkan pemahaman awal."
            "Namun, dalam setiap bahasan tertentu, buatlah header dengan format ##header untuk memudahkan pembaca bahwa 1 bahasan itu membahas tentang apa."
            "Gunakan enter di setiap header dan paragraf untuk kejelasan dan estetika."
            "Jika terdapat informasi yang lebih enak untuk dibuat list, maka buat informasi itu menjadi format poin-poin\n\n"
            f"Teks Materi:\n---\n{text}\n---\n\n"
            "Silakan buat ringkasannya:"
        )
        response = model.generate_content(user_query)
        respon = response.text
        return respon
    except Exception as e:
        return f"Terjadi kesalahan saat membuat ringkasan: {str(e)}"

        
def entry_form():
    # load_dotenv()###

    st.markdown(
    """
    <style>
      [data-testid="stSidebar"] { display: none; }
      .block-container {
          max-width: 1200px;  /* ubah sesuai kebutuhan */
          padding-left: 3rem;
          padding-right: 3rem;
          padding-top: 15rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
    )

    st.session_state.setdefault("uploaded", False)
    st.session_state.setdefault("conversations", None)

    if not st.session_state.get("uploaded"):
        with st.form("entry_form", clear_on_submit=False):
            st.header("📥 Silakan Unggah PDF atau Masukkan Link YouTube")
            pdf_local = st.file_uploader("Unggah file PDF", type=["pdf"], key="form_pdf", accept_multiple_files=True)
            yt_local  = st.text_input("Masukkan link YouTube", key="form_yt")
            submit = st.form_submit_button("Submit")

            if submit:
                if not (pdf_local or yt_local):
                    st.error("⚠️ Harap upload PDF atau masukkan link YouTube dulu.")
                    return
                
                else:
                    with st.spinner("Processing..."):
                        # Ambil teks PDFs atau link YouTube
                        raw = ""
                        if pdf_local:
                            raw = get_pdf_text(pdf_local)
                        elif yt_local:
                            raw = get_yt_text(yt_local)

                        if not raw or not raw.strip():
                            st.error("Gagal mengekstrak teks dari sumber yang diberikan.")
                            return
                        # Ambil teks chunks
                        chunks = get_text_chunks(raw)
                        # Buat vector database
                        vectorDB = get_vectorDB(chunks)
                        # Buat conversation chain
                        conversation = get_conversation_chain(vectorDB)
                        # Buat summary
                        initial_summary = generate_summary(raw)

                        st.session_state.conversations = conversation
                        st.session_state.initial_summary = initial_summary
                        st.session_state.raw_text = raw
                        st.session_state.text_chunks = chunks
                        st.session_state.messages = []
                        st.session_state.uploaded = True
                        st.rerun()
        st.stop()