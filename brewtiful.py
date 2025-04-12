# --- 1. Set-Up

# --- 1.1 Import Required Libraries ---
# Standard Library Imports
import os
from pathlib import Path
import yaml

# Third-Party Imports
import streamlit as st
from dotenv import load_dotenv

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory

# --- 1.2 Load Environment Variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 2. Define Functions and Variables ---

# --- 2.1 Initialize Session State ---  
def initialize_session_state():
    """Initialize session state variables if they do not exist."""
    if "all_notes" not in st.session_state:
        st.session_state.all_notes = []
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = None
    if "db" not in st.session_state:
        st.session_state.db = None
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "memory" not in st.session_state:
        st.session_state.memory = None
    if "user_query" not in st.session_state:
        st.session_state.user_query = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

# --- 2.2  Load and Preprocess Notes ---
def load_and_preprocess_notes(notes_dir="Notes"):
    """
    Load and preprocess markdown notes from the specified directory.

    Args:
        notes_dir (str): Path to the directory containing markdown files.

    Returns:
        list: A list of tuples containing filename, content, and metadata.
    """
    all_notes = []
    notes_path = Path(notes_dir)

    if not notes_path.exists() or not notes_path.is_dir():
        st.error(f"Error: '{notes_dir}' is not a valid directory.")
        return []

    markdown_files = list(notes_path.rglob("*.md"))

    if not markdown_files:
        st.warning(f"No markdown files found in '{notes_dir}'.")
        return []

    for file_path in markdown_files:
        try:
            # Skip README.md
            if file_path.name.lower() == "readme.md":
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract YAML front matter
            if content.startswith("---"):
                end_index = content.find("---", 3)
                if end_index != -1:
                    yaml_content = content[3:end_index].strip()
                    metadata = yaml.safe_load(yaml_content) if yaml_content else {}
                    content = content[end_index + 3:].strip()
                else:
                    metadata = {}
            else:
                metadata = {}

            all_notes.append((file_path.name, content, metadata))
        except Exception as e:
            st.error(f"Error reading or processing {file_path}: {e}")
    return all_notes

# --- 2.3 Split Documents ---
def split_documents(notes_data, chunk_size=1000, chunk_overlap=50):
    """
    Split notes into smaller chunks for processing.

    Args:
        notes_data (list): List of tuples containing filename, content, and metadata.
        chunk_size (int): Maximum size of each chunk.
        chunk_overlap (int): Overlap between chunks.

    Returns:
        list: A list of Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = []
    for filename, content, metadata in notes_data:
        split_texts = text_splitter.split_text(content)
        for text in split_texts:
            doc_metadata = {"source": filename, **metadata}
            docs.append(Document(page_content=text, metadata=doc_metadata))
    return docs

# --- 2.4 Filter Documents ---
def filter_documents(documents, selected_title=None, selected_categories=None, selected_tags=None):
    """
    Filter documents based on title, categories, and tags.

    Args:
        documents (list): List of Document objects.
        selected_title (str): Title to filter by.
        selected_categories (list): Categories to filter by.
        selected_tags (list): Tags to filter by.

    Returns:
        list: A list of filtered Document objects.
    """
    filtered_docs = documents

    if selected_title:
        filtered_docs = [doc for doc in filtered_docs if doc.metadata.get('title') == selected_title]

    if selected_categories:
        # Check if selected categories are a subset of document categories
        filtered_docs = [
            doc for doc in filtered_docs
            if doc.metadata.get('categories') is not None and set(selected_categories).issubset(set(doc.metadata.get('categories')))
        ]

    if selected_tags:
        # Check if selected tags are a subset of document tags
        filtered_docs = [
            doc for doc in filtered_docs
            if doc.metadata.get('tags') is not None and set(selected_tags).issubset(set(doc.metadata.get('tags')))
        ]

    return filtered_docs

# --- 2.5 Format Documents ---
def format_docs(docs):
    """
    Format documents for display.

    Args:
        docs (list): List of Document objects.

    Returns:
        str: Formatted string representation of documents.
    """
    return "\n\n".join(f"Source: {doc.metadata['source']}\nContent: {doc.page_content}" for doc in docs)

# --- 2.6 Retrieve Chat History ---
def get_chat_history(memory):
    """
    Retrieve chat history from memory.

    Args:
        memory (ConversationBufferMemory): Memory object containing chat history.

    Returns:
        str: Formatted chat history.
    """
    messages = memory.chat_memory.messages
    return "\n".join([f"{m.type}: {m.content}" for m in messages])

# --- 2.7 Create LangChain Processing Chain  ---
def create_chain(llm, retriever, memory):
    """
    Create a LangChain processing chain.

    Args:
        llm (ChatGoogleGenerativeAI): Language model.
        retriever (FAISS): Document retriever.
        memory (ConversationBufferMemory): Memory object.

    Returns:
        dict: LangChain processing chain.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer based on the context and the chat history. If you don't know, say so.\n\nContext:\n{context}\n\nChat History:\n{chat_history}"),
        ("user", "{question}")
    ])

    return (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnableLambda(lambda x: x),
            "chat_history": RunnableLambda(lambda x: get_chat_history(memory)),
        }
        | prompt
        | (llm if llm else RunnableLambda(lambda x: x))
    )
# --- 3 Main Application Logic ---

# --- 3.1 Main Function Definition ---
def main():
    """Main function for the Streamlit app."""
    st.title("Welcome to Brewtiful ☕")
    st.subheader("What questions do you have for us?")

    # --- Step 1. Session State Initialization ---
    initialize_session_state()

    # --- Step 2. Data Loading and Processing---
    if not st.session_state.all_notes:
        st.session_state.all_notes = load_and_preprocess_notes()
        st.session_state.documents = split_documents(st.session_state.all_notes) if st.session_state.all_notes else []

    # --- LangChain Component Setup (Steps 3-6) ---
    if st.session_state.documents:
    # --- Step 3. Embeddings Initialization ---
        if not st.session_state.embeddings:
            st.session_state.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    #  --- Step 4. Vector Store Creation ---
        if not st.session_state.db:
            st.session_state.db = FAISS.from_documents(st.session_state.documents, st.session_state.embeddings)
    # --- Step 5. LLM Initialization ---
        if not st.session_state.llm and GOOGLE_API_KEY:
            st.session_state.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", google_api_key=GOOGLE_API_KEY, temperature=0.5)
        elif not st.session_state.llm:
            st.session_state.llm = None
    # --- Step 6. Memory Initialization ---
        if not st.session_state.memory:
            st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, input_key="question")
    else:
        st.warning("No documents available.")
        return

    # --- Step 7. User Interface Setup (Sidebar Filters & Preloaded Prompts) ---
    with st.sidebar:
        st.header("Filters")

        unique_titles = []
        unique_categories = []
        unique_tags = []

        for doc in st.session_state.documents:
            title = doc.metadata.get('title')
            if title is not None:
                unique_titles.append(str(title))
            categories = doc.metadata.get('categories')
            if categories:
                unique_categories.extend(categories)
            tags = doc.metadata.get('tags')
            if tags:
                unique_tags.extend(tags)

        unique_titles = sorted(list(set(unique_titles)))
        unique_categories = sorted(list(set(unique_categories)))
        unique_tags = sorted(list(set(unique_tags)))

        selected_title = st.selectbox("Select Title", options=[None] + unique_titles)
        selected_categories = st.multiselect("Select Categories", options=unique_categories)
        selected_tags = st.multiselect("Select Tags", options=unique_tags)

    # --- Preloaded Prompts---
    st.write("Quick Questions:")
    col1, col2, col3 = st.columns(3)

    if col1.button("Can you provide specific details about brewtiful?", key="button1"):
        st.session_state.user_query = "Can you provide specific details about brewtiful?"
    if col2.button("What is the current forecast for Enterprise clients?", key="button2"):
        st.session_state.user_query = "What is the current forecast for Enterprise clients?"
    if col3.button("Describe the ongoing activities related to the cloud.", key="button3"):
        st.session_state.user_query = "Describe the ongoing activities related to the cloud."

    # --- Step 8. User Interaction (Chat Interface) ---
    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get new user input
    user_query_input = st.chat_input("Ask a question...")
    if user_query_input:
        st.session_state.user_query = user_query_input

    # --- Query Handling (Steps 9-12) ---
    if st.session_state.user_query:
        # Display user query 
        with st.chat_message("user"):
            st.markdown(st.session_state.user_query)
        # Add user query to message history
        st.session_state.messages.append({"role": "user", "content": st.session_state.user_query})

    # --- Step 9. Dynamic Filtering and Retrieval Setup ---
        filtered_docs = filter_documents(st.session_state.documents, selected_title, selected_categories, selected_tags)

        if filtered_docs:
            db_filtered = FAISS.from_documents(filtered_docs, st.session_state.embeddings)
            dynamic_retriever = db_filtered.as_retriever(search_kwargs={"k": 3})
        else:
            # If filtering removes all docs, create a dummy retriever and warn
            dynamic_retriever = RunnableLambda(lambda x: []) # Returns an empty list
            st.warning("No documents match the filters.") # Warning displayed in main area

    # --- Step 10. Chain Creation and Invocation ---
        # Proceed only if documents were found after filtering
        if filtered_docs:
            chain = create_chain(st.session_state.llm, dynamic_retriever, st.session_state.memory)
            try:
                with st.spinner("Thinking..."):
                    response_obj = chain.invoke(st.session_state.user_query)
                # Extract the content from the response object
                response_content = response_obj.content if hasattr(response_obj, 'content') else str(response_obj)

    # --- Step 11. Response Handling (Success) ---
                # Add interaction to memory
                st.session_state.memory.chat_memory.add_user_message(st.session_state.user_query)
                st.session_state.memory.chat_memory.add_ai_message(response_content)

                # Display assistant response
                with st.chat_message("assistant"):
                    # Use the extracted string content
                    st.markdown(response_content)
                # Add assistant response to message history
                st.session_state.messages.append({"role": "assistant", "content": response_content})

    # --- Step 12. State Reset ---
                if st.session_state.user_query != user_query_input:
                    st.session_state.user_query = None
            except Exception as e:
                # Error Handling (Part of Step 11)
                st.error(f"An error occurred: {e}")

# --- 3.2 Run Application ---
if __name__ == "__main__":
    main()