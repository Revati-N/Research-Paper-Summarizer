import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAI, ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import tempfile
import pandas as pd

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="📄Chat with Multiple Research Papers", layout="wide")
st.title("📄 Chat with Multiple Research Papers")

# Function to extract text from uploaded PDF
def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

# Function to extract research paper metadata using LLM
def extract_paper_metadata(pdf_text, pdf_name):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
        convert_system_message_to_human=True
    )
    
    metadata_prompt = PromptTemplate(
        input_variables=["pdf_text", "pdf_name"],
        template="""
        You are an expert research paper analyzer. Extract the following information from this research paper text.
        Format your response as a JSON dictionary with these exact keys:
        
        - Year: (publication year)
        - Authors: (list of authors)
        - Title: (full title of the paper)
        - Keywords: (main keywords or topics)
        - Methodology: (brief description of methods used)
        - Key_Findings: (main results or conclusions)
        - Preprocessing: (data preprocessing steps if applicable)
        - Evaluation_Metrics: (metrics used to evaluate results)
        - Results: (brief summary of numerical or qualitative results)
        - Advantages: (strengths of the approach)
        - Other_Details: (any other specific details)
        - Limitations: (weaknesses or limitations mentioned)
        
        Research paper text: {pdf_text}
        PDF filename: {pdf_name}
        
        Return ONLY the JSON dictionary with no additional text before or after. If any field cannot be determined, use "Not specified in the paper".
        """
    )
    
    chain = LLMChain(llm=llm, prompt=metadata_prompt)
    
    try:
        response = chain.run({"pdf_text": pdf_text[:50000], "pdf_name": pdf_name})
        # Try to convert the response to a proper dictionary
        import json
        import re
        
        # Clean up the response to ensure it's valid JSON
        # Remove any markdown code block markers
        response = re.sub(r'```json|```', '', response).strip()
        
        # Parse the JSON
        metadata = json.loads(response)
        return metadata
    except Exception as e:
        st.error(f"Error extracting metadata: {str(e)}")
        return {
            "Year": "Error", "Authors": "Error", "Title": "Error",
            "Keywords": "Error", "Methodology": "Error", "Key_Findings": "Error",
            "Preprocessing": "Error", "Evaluation_Metrics": "Error", "Results": "Error",
            "Advantages": "Error", "Other_Details": "Error", "Limitations": "Error"
        }

# Create the sidebar for PDF uploads
with st.sidebar:
    st.header("Upload Research Papers")
    uploaded_pdfs = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if uploaded_pdfs:
        st.subheader("Uploaded PDFs:")
        for i, pdf in enumerate(uploaded_pdfs):
            st.write(f"{i+1}. {pdf.name}")

# Main area for results and question answering
question = st.text_input("Ask a question about the PDFs:")

# Process PDFs
if uploaded_pdfs:
    with st.spinner("Processing PDFs..."):
        # Extract text from all PDFs
        pdf_texts = []
        metadata_list = []
        
        # Process each PDF
        for i, pdf in enumerate(uploaded_pdfs):
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf.getvalue())
                tmp_path = tmp.name
            
            # Extract text from the temporary file
            with open(tmp_path, 'rb') as f:
                pdf_text = extract_pdf_text(f)
                pdf_texts.append(pdf_text)
                
                # Extract metadata from the PDF text
                with st.spinner(f"Analyzing {pdf.name}..."):
                    metadata = extract_paper_metadata(pdf_text, pdf.name)
                    metadata_list.append(metadata)
            
            # Clean up the temporary file
            os.unlink(tmp_path)
        
        # Create DataFrame for displaying metadata
        df = pd.DataFrame(metadata_list)
        
        # Display metadata in table format
        st.subheader("Research Paper Analysis:")
        st.dataframe(df, use_container_width=True)
        
        # Combine all PDF texts
        combined_text = "\n\n".join(pdf_texts)
        
        # Save to session state
        st.session_state.pdf_texts = combined_text

# Answer questions
if question and uploaded_pdfs:
    with st.spinner("Generating answer..."):
        # Correct Gemini model name
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
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