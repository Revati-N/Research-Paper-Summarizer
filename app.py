import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import tempfile

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="📄Chat with Multiple Research Papers", layout="wide")
st.title("📄 Chat with Multiple Research Papers")

# Function to extract text from uploaded PDF
def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

# UI for PDF uploads
uploaded_pdfs = st.file_uploader("Upload your PDFs", type="pdf", accept_multiple_files=True)
question = st.text_input("Ask a question about the PDFs:")

# Process PDFs
if uploaded_pdfs:
    with st.spinner("Processing PDFs..."):
        # Extract text from all PDFs
        pdf_texts = []
        
        # Display uploaded PDFs
        st.subheader("Uploaded PDFs:")
        for i, pdf in enumerate(uploaded_pdfs):
            st.write(f"{i+1}. {pdf.name}")
            
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf.getvalue())
                tmp_path = tmp.name
            
            # Extract text from the temporary file
            with open(tmp_path, 'rb') as f:
                pdf_text = extract_pdf_text(f)
                pdf_texts.append(pdf_text)
            
            # Clean up the temporary file
            os.unlink(tmp_path)
        
        # Combine all PDF texts
        combined_text = "\n\n".join(pdf_texts)
        
        # Save to session state
        st.session_state.pdf_texts = combined_text

# Answer questions
if question and uploaded_pdfs:
    with st.spinner("Generating answer..."):
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
            template="""
            Context: {context}
            
            Based on the information provided in the multiple PDFs above, please answer this question thoroughly:
            
            Question: {question}
            
            When answering, if information comes from a specific document, please mention which document it comes from.
            If the question cannot be answered based on the provided documents, please state that clearly.
            
            Answer:
            """
        )

        # LLMChain setup without memory
        chain = LLMChain(llm=llm, prompt=prompt_template)

        # Run the chain
        response = chain.run({"context": st.session_state.pdf_texts, "question": question})

        # Show result
        st.subheader("Answer:")
        st.write(response)

elif question and not uploaded_pdfs:
    st.warning("Please upload at least one PDF file first.")