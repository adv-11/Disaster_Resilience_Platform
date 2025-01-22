import streamlit as st

st.title("🤖 Resilio Chatbot: ")
st.subheader("A Personal Assistant for Disaster Relief")
st.markdown("---")

from huggingface_hub import InferenceClient
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceHubEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceEndpoint 

# Load environment variables
HF_TOKEN = os.getenv('HF_TOKEN')

# Initialize Streamlit app

# Sidebar for document upload
with st.sidebar:
    st.header("RAG Functionality")
    uploaded_file = st.file_uploader("Upload a document (PDF only)", type=["pdf"])

# Initialize document processing variables
documents = None
vector_store = None
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    loader = PyPDFLoader(temp_file_path)

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    embeddings = HuggingFaceHubEmbeddings(huggingfacehub_api_token=HF_TOKEN)
    vector_store = FAISS.from_documents(texts, embeddings)

    st.sidebar.success("Document uploaded and processed successfully!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant specialized in disaster relief. Please provide accurate and concise information. If anything except disaster relief is asked, say you dont know and tell the user to ask about disaster relief."},
        {"role": "assistant", "content": "Hello 👋 Hope you are doing well. How may I assist you today?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# User prompt input
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if documents is None:
                # No document uploaded - basic response
                client = InferenceClient(api_key=HF_TOKEN)

                stream = client.chat.completions.create(
                    model="meta-llama/Llama-3.2-1B-Instruct",
                    messages=st.session_state.messages,
                    max_tokens=512,
                    temperature=0.01,
                    top_p=0.9,
                    stream=True
                )

                placeholder = st.empty()
                full_response = ''
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response)

                if full_response.strip():
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                # Document uploaded - RAG-based response
                qa_chain = RetrievalQA.from_chain_type(
                    llm=HuggingFaceEndpoint(
                        repo_id="meta-llama/Llama-3.2-1B-Instruct",
                        max_length=512,
                        temperature=0.01,
                        top_p=0.9,
                        huggingfacehub_api_token=HF_TOKEN,
                    ),
                    chain_type="stuff",
                    retriever=vector_store.as_retriever()
                )

                response = qa_chain({"query": prompt})
                full_response = response["result"]
                st.write(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
