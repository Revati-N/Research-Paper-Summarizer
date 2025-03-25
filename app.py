import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS # Runs locally
from langchain.llms import ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import conversational_retrieval

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter =CharacterTextSplitter(
        separator="\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function =len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")
    vectorstore = FAISS.from_texts(texts = text_chunks, embedding= embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ollama()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = conversational_retrieval.from_llm(
        llm = llm,
        retriever = vectorstore.as_retriever(),
        memory = memory
    )
    return conversation_chain

def main():
    load_dotenv() 
    st.set_page_config(page_title="Research Paper Reviewer", page_icon=":memo:")
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    st.header("Research Paper Chat :memo:")
    st.text_input("Ask a question about your papers: ")

    with st.sidebar: # DO NOT ADD A PARENTHESIS HERE
        st.subheader("Papers: ")
        pdf_docs = st.file_uploader("Upload the papers and click 'Process'", accept_multiple_files=True)
        
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get text
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # Conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)


if __name__ == '__main__':
    main()