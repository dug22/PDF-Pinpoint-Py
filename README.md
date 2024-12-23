# **About**
<p align="justify">
PDF Pinpoint Py is the Python variation of PDF Pinpoint. You can find the original repository here [PDF Pinpoint](https://github.com/dug22/PDF-Pinpoint)
As previously stated, PDF Pinpoint Py is a small-scale and simple local chatbot tool powered by retrieval-augmented generation (RAG). It leverages large language models to process and train on multiple PDF documents, 
enabling users to efficiently find the answers they're looking for across various PDF documents. 
</p>

# Getting Started 
### **Prerequisites**
* Ensure you have Git installed
* Ensure you have Python 3.9 > installed.
* Install Ollama and a Llama 3.2 or 3.1 model, and Nomic Embedding Model.

### **Quickstart**
1. Git clone this repository
2. Ensure you have Ollama installed and have a Llama 3.2 or 3.1 model, and Nomic Embedding Model installed.
3. Install the following Python packages listed in requirements.txt
4. All documents once uploaded are loaded into the following directory /pdfs.
5. Start your application and go to localhost:5000 with a web browser.

# **Usage**
PDF Pinpoint Py allows you to do the following:

   * Upload and manage multiple PDF documents with ease.
   * Search for answers to specific questions by extracting relevant content directly from your uploaded documents.
   * Identify, compare, and analyze relationships between the documents to uncover possible patterns and connections.
   * Enhance productivity for academic, legal, or business purposes with PDF Pinpoint.
   * Does not require an internet connection to run this application, which respects user privacy.

# **URL Endpoints:**
   1. localhost:5000 accesses the main RAG chatbot application.
   2. localhost:5000/upload endpoint to upload documents.
   3. localhost:5000/documents accesses a list of documents loaded into the application.
   4. localhost:5000/delete/file_name deletes a file from the given repository.

# **Contributions**
If you'd like to contribute to this repository, feel free to open a pull request with your suggestions, bug fixes, or enhancements. Contributions are always welcome!
