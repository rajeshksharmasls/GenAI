## RAG Based Chatbot With Streamlit GUI

# Importing the important libraries
import streamlit as st								                            # For building the web application
from PyPDF2 import PdfReader							                        # For reading and extracting text from PDF files
from langchain.text_splitter import RecursiveCharacterTextSplitter 		        # For splitting long texts into manageable chunks
from langchain.prompts.chat import SystemMessagePromptTemplate                  # For creating templates for the Qwen model prompts
from langchain.prompts.chat import HumanMessagePromptTemplate, AIMessagePromptTemplate # For creating templates for the Qwen model prompts
from langchain.prompts import ChatPromptTemplate				                # For creating templates for the Qwen model prompts
from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings   	# For embedding generation using the SpaCy NLP model
from langchain_community.vectorstores import FAISS				                # For efficient vector-based storage and retrieval
from langchain.tools.retriever import create_retriever_tool			            # For building retrieval tools for question answering
from langchain.agents import create_react_agent                                 # For creating agent
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline          # For Qwen model integration  
from langchain_huggingface import HuggingFacePipeline                           # Pipeline for HuggingPace
from dotenv import load_dotenv							                        # For loading environment variables from a .env file
import os									                                    # For interacting with the operating system
import huggingface_hub                                                          # For HuggingFace
from huggingface_hub import hf_hub_download                                     # For login into HuggingFace
import logging                                                                  # For logging
from langchain.schema import SystemMessage, HumanMessage, AIMessage             # For formatting the prompt messages
from langchain.docstore.document import Document                                # For Document processing

# For logging
# 
# logging.basicConfig(level=logging.DEBUG)  # Set DEBUG level globally

# To handle potential shared library errors
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

load_dotenv() # Load environment variables

# Log into Hugging Face
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Qwen model and tokenizer
model_name="Qwen/Qwen2.5-0.5B-Instruct"
qwen_model = AutoModelForCausalLM.from_pretrained(model_name)
qwen_tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=HF_TOKEN)

# Create a Hugging Face pipeline for text generation
hf_pipeline = pipeline(
    "text-generation", model=qwen_model, tokenizer=qwen_tokenizer, max_length=512, device="cpu"
)

# Wrap the Hugging Face pipeline in LangChain's HuggingFacePipeline
qwen_llm = HuggingFacePipeline(pipeline=hf_pipeline)

# Initialize the embedding model 
embeddings = SpacyEmbeddings(model_name="en_core_web_lg")

# Function to read text from uploaded PDF files
def pdf_read(pdf_doc):
    text = ""
    # Loop through each uploaded PDF file
    for pdf in pdf_doc:     
        pdf_reader = PdfReader(pdf)
        # Extract text from each page of the PDF
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Function to split the extracted text into smaller chunks
def get_chunks(text):
    # Chunk size is 1000 characters with an overlap of 200 characters
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

# Function to create a FAISS vector store for storing text embeddings
def vector_store(text_chunks):
    # Create documents using LangChain's Document class
    documents = [Document(page_content=chunk, metadata={}) for chunk in text_chunks]
    
    # Convert documents into embeddings and store them in FAISS
    vector_store = FAISS.from_documents(documents, embedding=embeddings)
    
    # Save the FAISS index locally for later retrieval
    vector_store.save_local("faiss_db")

# Function to handle question answering using the Qwen model and retriever tool
def get_conversational_chain(retrieval_tool, user_question):
    
     # Format the prompt with the required variables: user question and tools
    tool_names = "pdf_extractor"

    print("Tool Names", tool_names)
    
    # Define individual message templates
    system_message_template = SystemMessagePromptTemplate.from_template(
        """You are a helpful assistant equipped with tools to answer questions.
          Use the available tools effectively. If the answer cannot be found in the provided context, 
          reply with: "The answer is not available in the context." Do not provide incorrect or misleading answers."""
   )
    
    # Format the system message with the tool_names variable
    print("Before System Message")
    system_message = system_message_template.format()

    print("System Message:", system_message)
    
    human_message = HumanMessagePromptTemplate.from_template("{input}")

    print("Human Message:", human_message)

    assistant_initial_message = AIMessagePromptTemplate.from_template("Let me check that for you...")

    assistant_scratchpad_message = AIMessagePromptTemplate.from_template("Checking")

    print("User Question", user_question)

    # Create the ChatPromptTemplate from these message templates
    prompt = ChatPromptTemplate.from_messages(
        [
            system_message,
            human_message,
            assistant_initial_message,
            assistant_scratchpad_message
        ]
    )

     
    #formatted_prompt = prompt.format_messages(input=user_question, tool_names=tool_names )
    formatted_prompt = prompt.format_messages(input=user_question)

    print("FORMATTED TEXT", formatted_prompt)

    # Initialize the agent with the retrieval tool
    agent = create_react_agent(
       llm=qwen_llm,
       tools=retrieval_tool,
       prompt=formatted_prompt
    )

    print("Before INVOKE")

    # Generate a response to the user's question
    response = agent.invoke({"input": user_question})

    print("RESPONSE", response['output'])

    # Display the agent's response
    st.write("Reply: ", response['output'])

# Function to handle user inputs and process queries
def user_input(user_question):
    try:
        # Load FAISS vector store created earlier
        new_db = FAISS.load_local("faiss_db", embeddings, allow_dangerous_deserialization=True)
        retriever = new_db.as_retriever()

        # Define a retrieval tool
        retrieval_tool = create_retriever_tool(
            retriever, "pdf_extractor", "This tool answers queries from the PDF content."
        )

        # Use the conversational chain to process the query
        get_conversational_chain(retrieval_tool, user_question)

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Main function to define the Streamlit UI and handle user interactions
def main():
    # Set the page title for the Streamlit app
    st.set_page_config("Chat PDF")
    st.header("RAG-based Chat with PDF")  # Display the app's header

    # Input field for the user to ask a question about the PDF content
    user_question = st.text_input("Ask a Question from the PDF Files")

    # If the user enters a question, process it
    if user_question:
        user_input(user_question)

    # Sidebar for uploading PDF files
    with st.sidebar:
        st.title("Menu:")  # Sidebar menu title
        # File uploader for the user to upload multiple PDF files
        pdf_doc = st.file_uploader(
            "Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True
        )
        # Button to process the uploaded PDF files
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):  # Show a spinner while processing
                # Extract text from PDFs and create chunks
                raw_text = pdf_read(pdf_doc)
                text_chunks = get_chunks(raw_text)
                # Store the chunks in the FAISS vector store
                vector_store(text_chunks)
                
                st.success("Done")  # Indicate successful processing

# Run the app when the script is executed
if __name__ == "__main__":
    main()
