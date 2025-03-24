import streamlit as st
from dotenv import load_dotenv

def main():
    load_dotenv() 
    st.set_page_config(page_title="Research Paper Reviewer", page_icon=":memo:")

    st.header("Research Paper Chat :memo:")
    st.text_input("Ask a question about your papers: ")

    with st.sidebar: # DO NOT ADD A PARENTHESIS HERE
        st.subheader("Papers: ")
        st.file_uploader("Upload the pdfs here and click 'Process'")
        st.button("Process")

if __name__ == '__main__':
    main()