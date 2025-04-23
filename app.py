import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="Chat with PDF using Gemini", layout="wide")
st.title("📄 Chat with PDF using Gemini 🤖")

# Function to extract text from uploaded PDF
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

# UI for PDF upload and user input
uploaded_pdf = st.file_uploader("Upload your PDF", type="pdf")
question = st.text_input("Ask a question about the PDF:")

if uploaded_pdf and question:
    with st.spinner("Processing..."):
        pdf_text = extract_pdf_text(uploaded_pdf)

        # ✅ Correct Gemini model name here
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",  # ✅ Use this model
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7,
            convert_system_message_to_human=True
        )

        # Prompt template
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        )

        # Conversation memory
        memory = ConversationBufferMemory(input_key="question", memory_key="chat_history")

        # LLMChain setup
        chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)

        # Run the chain
        response = chain.run({"context": pdf_text, "question": question})

        # Show result
        st.subheader("Answer:")
        st.write(response)
