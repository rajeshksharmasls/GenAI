from fastapi import FastAPI, HTTPException                                      # To create API endpoints and error handling
from pydantic import BaseModel                                                  # To define request/response schemas for validation
import os                                                                       # For handling file paths and system-related operations
import torch                                                                    # For model inference
from transformers import AutoTokenizer, AutoModelForCausalLM                    # For Qwen model integration  
from langchain_community.document_loaders import PyPDFLoader                    # Document loader integration
from langchain.text_splitter import RecursiveCharacterTextSplitter              # For splitting long texts into manageable chunks
from langchain_community.vectorstores import FAISS                              # For efficient vector-based storage and retrieval
from dotenv import load_dotenv							                        # For loading environment variables from a .env file
from langchain.docstore.document import Document                                # For Document processing
from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings   	# For embedding generation using the SpaCy NLP model


# To handle potential shared library errors
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

load_dotenv() # Load environment variables

# Log into Hugging Face
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize FastAPI
app = FastAPI(title="RAG Based Chat with PDF Document and Query API", version="1.0")

# Load Model
device = torch.device("cpu")
checkpoint = "Qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
base_model = AutoModelForCausalLM.from_pretrained(
    checkpoint,
    device_map=device,
    torch_dtype=torch.float32
)

# API Models
class QueryRequest(BaseModel):
    query: str

# Ingest PDFs and Create Vector Database
@app.post("/ingest/")
async def ingest_pdfs():
    """Ingest PDF files and create embeddings for querying."""
    try:
        documents = []
        for root, dirs, files in os.walk("PDFFILES"):
            for file in files:
                if file.endswith(".pdf"):
                    print(f"Loading {file}")
                    loader = PyPDFLoader(os.path.join(root, file))
                    documents.extend(loader.load())
        
        if not documents:
            raise HTTPException(status_code=400, detail="No PDFs found in the 'PDFFILES' directory.")

        print("Splitting into chunks")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        text_chunks = text_splitter.split_documents(documents)

        print("Creating embeddings")
        # Initialize the embedding model 
        embeddings = SpacyEmbeddings(model_name="en_core_web_lg")
        
        # Create documents using LangChain's Document class
        documents = [Document(page_content=chunk.page_content, metadata={}) for chunk in text_chunks]
    
        # Convert documents into embeddings and store them in FAISS
        vector_store = FAISS.from_documents(documents, embedding=embeddings)
    
        # Save the FAISS index locally for later retrieval
        vector_store.save_local("faiss_db")

        faiss_db = None  # Clear memory

        return {"message": "Ingestion is complete. You can now query the PDFs."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Query the Database
@app.post("/query/")
async def query_documents(request: QueryRequest):
    """Query the ingested documents."""
    try:
    
        embeddings = SpacyEmbeddings(model_name="en_core_web_lg")

        # Load FAISS vector store created earlier
        new_db = FAISS.load_local("faiss_db", embeddings, allow_dangerous_deserialization=True)
        retriever = new_db.as_retriever()

        docs = retriever.get_relevant_documents(request.query)

        if not docs:
            return {"query": request.query, "response": "No relevant documents found."}

        return {
            "query": request.query,
            "response": [doc.page_content for doc in docs]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Ingestion and Query API!"}



