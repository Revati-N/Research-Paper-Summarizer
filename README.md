# Research Paper Analyzer (Terminal-Based with Local LLM)

This project is a Python-based AI tool that extracts structured information from research papers and enables users to ask follow-up questions. It runs entirely in the terminal and features:

- PDF Upload & Text Extraction – Reads research papers using pypdf.
- AI-Powered Analysis – Uses a local LLM (Mistral/Llama 2 via llama.cpp) to extract details such as Year, Title, Keywords, Dataset, Models, Methodology, Contribution, and Additional Notes in a table format.
- Interactive Q&A – Allows users to ask further questions about the paper, with the LLM responding intelligently based on extracted content.

This implementation ensures privacy and efficiency by running the LLM completely offline using langchain and llama-cpp-python. 🚀
