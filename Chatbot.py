import streamlit as st
from entry_helper import entry_form
from dotenv import load_dotenv

def chat_page():
    st.set_page_config(page_title="Chatbot", page_icon="🤖")
    st.title("📑Study Helper AI📚")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Hasil summary
    if not st.session_state.messages:
        initial_summary = st.session_state.get(
            "initial_summary", "Tidak ada ringkasan tersedia"
        )
        st.session_state.messages.append({
            "role":"assistant",
            "content":initial_summary
        })
    
    # History chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input user
    prompt = st.chat_input("i'll be waiting for your questions...")
    if prompt:
        st.session_state.messages.append({
            "role":"user",
            "content":prompt
        })
        with st.chat_message("User"):
            st.markdown(prompt)

        # Ambil respon dari conversation chain
        with st.chat_message("assistant"):
            place_holder = st.empty()
            full_response = ""
            chain = st.session_state.get("conversations")
            if chain:
                stream = chain.stream({"question":prompt})
                for chunk in stream:
                    if "answer" in chunk:
                        full_response += chunk["answer"]
                        place_holder.markdown(full_response + "|")
                
                place_holder.markdown(full_response)
            else:
                full_response = "Sorry, this chat is inactive. Please process the documents first."
                place_holder.markdown(full_response)
            
            st.session_state.messages.append({
                    "role":"assistant",
                    "content":full_response
                })

def main():

    if "uploaded" not in st.session_state:
        st.session_state.uploaded = False

    if not st.session_state.uploaded:
        entry_form()
    else:
        chat_page()

if __name__ == "__main__":
    load_dotenv()
    main()