from flask import Flask, request, jsonify, render_template
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain_ollama import OllamaLLM as OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.docstore import InMemoryDocstore
import os
import pandas as pd
import json
import numpy as np
import uuid


app = Flask(__name__)

EMBEDDINGS_BASE_URL = "http://localhost:11434"
EMBEDDINGS_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2"

embeddings = OllamaEmbeddings(base_url=EMBEDDINGS_BASE_URL, model=EMBEDDINGS_MODEL)
llm = OllamaLLM(base_url=EMBEDDINGS_BASE_URL, model=LLM_MODEL)

vector_store = None
DOCUMENT_STORAGE_LOC = os.path.join(os.getcwd(), "pdfs")
VECTOR_STORE_PATH = os.path.join(os.getcwd(), "vector_store.json")

os.makedirs(DOCUMENT_STORAGE_LOC, exist_ok=True)


def save_vector_store():
    global vector_store
    if vector_store:
        try:
            data = {
                "index": vector_store.index.serialize().decode(),
                "docstore": list(vector_store.docstore._dict.items())
            }
            with open(VECTOR_STORE_PATH, "w") as f:
                json.dump(data, f)
            print("Vector store saved successfully.")
        except Exception as e:
            print(f"Error saving vector store: {e}")



def load_vector_store():
    global vector_store
    try:
        if os.path.exists(VECTOR_STORE_PATH):
            with open(VECTOR_STORE_PATH, "r") as f:
                data = json.load(f)
            index = FAISS.deserialize_from_bytes(data["index"].encode())
            docstore = InMemoryDocstore({k: v for k, v in data["docstore"]})
            vector_store = FAISS(embeddings.embed_query, index, docstore, {})
        else:
            vector_store = FAISS.from_texts(["Initial document"], embeddings)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error loading vector store: {e}")
        vector_store = FAISS.from_texts(["Initial document"], embeddings)



def initialize_vector_store():
    global vector_store
    load_vector_store()
    for filename in os.listdir(DOCUMENT_STORAGE_LOC):
        if filename.endswith('.pdf'):
            file_path = os.path.join(DOCUMENT_STORAGE_LOC, filename)
            add_to_vector_store(file_path)
    save_vector_store()


@app.route('/documents', methods=['GET'])
def list_available_documents():
    files = [f for f in os.listdir(DOCUMENT_STORAGE_LOC) if f.endswith('.pdf')]
    return jsonify(files)


@app.route('/delete/<filename>', methods=['GET'])
def delete_pdf_document(filename):
    global vector_store
    file_path = os.path.join(DOCUMENT_STORAGE_LOC, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        if vector_store:
            to_delete = [
                key for key, doc in vector_store.docstore._dict.items()
                if doc.metadata.get('source', '').endswith(filename)
            ]
            for key in to_delete:
                vector_store.docstore._dict.pop(key, None)
                key_bytes = uuid.UUID(key).bytes
                vector_store.index.remove_ids(np.frombuffer(key_bytes, dtype=np.uint8))

            save_vector_store()
            return jsonify({"message": f"File {filename} deleted successfully from storage and vector store"})
    return jsonify({"error": "File not found"}), 404



def store_to_df(store):
    v_dict = store.docstore._dict
    data_rows = []
    for k, v in v_dict.items():
        doc_name = v.metadata.get('source', '').split('/')[-1]
        page_number = v.metadata.get('page', 0) + 1
        content = v.page_content
        data_rows.append({"chunk_id": k, "document": doc_name, "page": page_number, "content": content})
    return pd.DataFrame(data_rows)


@app.route('/upload', methods=['POST'])
def upload_pdf_document():
    if 'document' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        try:
            file_path = os.path.join(DOCUMENT_STORAGE_LOC, file.filename)
            file.save(file_path)
            add_to_vector_store(file_path)
            return jsonify({"message": "File uploaded and processed successfully.", "path": file_path}), 200
        except Exception as e:
            return jsonify({"error": f"Error uploading or processing the document: {str(e)}"}), 500

    return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400


@app.route('/question', methods=['GET'])
def ask_question():
    question = request.args.get('question')
    if not question:
        return "No question provided.", 400
    answer = question_service(question)
    return answer


def add_to_vector_store(file_path):
    global vector_store
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = TokenTextSplitter(chunk_size=12000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        vector_store.add_documents(texts)
        save_vector_store()
        print(f"Added {len(texts)} text chunks from {file_path} to the vector store.")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")


def question_service(question):
    try:
        related_docs = vector_store.similarity_search(question)
        if not related_docs:
            return "I'm sorry, but I couldn't find any relevant information to answer your question."

        context = "\n".join([doc.page_content for doc in related_docs])

        prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template=(
                "PDF Pinpoint is authorized to reference the PDF documents it manages to respond to "
                "any {question}, using {context} to deliver the most precise and accurate information "
                "for the user. Output your response in plain text."
            )
        )

        chain = prompt_template | llm | RunnablePassthrough()
        response = chain.invoke({"question": question, "context": context})
        return response
    except Exception as e:
        print(f"Error in question_service: {str(e)}")
        return "I'm sorry, but an error occurred while processing your question."


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    initialize_vector_store()
    app.run(debug=True)
