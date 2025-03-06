import os
import streamlit as st
from dotenv import load_dotenv
import openai
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Predefined Q&A dataset about Thoughtful AI
faq_data = [
    {
        "question": "What does the eligibility verification agent (EVA) do?",
        "answer": "EVA automates the process of verifying a patient's eligibility and benefits information in real-time, eliminating manual data entry errors and reducing claim rejections.",
    },
    {
        "question": "What does the claims processing agent (CAM) do?",
        "answer": "CAM streamlines the submission and management of claims, improving accuracy, reducing manual intervention, and accelerating reimbursements.",
    },
    {
        "question": "How does the payment posting agent (PHIL) work?",
        "answer": "PHIL automates the posting of payments to patient accounts, ensuring fast, accurate reconciliation of payments and reducing administrative burden.",
    },
    {
        "question": "Tell me about Thoughtful AI's Agents.",
        "answer": "Thoughtful AI provides a suite of AI-powered automation agents designed to streamline healthcare processes. These include Eligibility Verification (EVA), Claims Processing (CAM), and Payment Posting (PHIL), among others.",
    },
    {
        "question": "What are the benefits of using Thoughtful AI's agents?",
        "answer": "Using Thoughtful AI's Agents can significantly reduce administrative costs, improve operational efficiency, and reduce errors in critical processes like claims management and payment posting.",
    },
]


def init_chroma():
    """Initialize ChromaDB client and collection"""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Define OpenAI embedding function for Chroma to use
    embed_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
    )

    # Initialize ChromaDB client with new configuration
    client = chromadb.PersistentClient(path="data")

    # Create a collection for FAQs
    collection = client.get_or_create_collection(
        name="thoughtful_faq", embedding_function=embed_fn
    )

    # Add all FAQ Q&A to the collection
    for idx, item in enumerate(faq_data):
        q_text = item["question"]
        ans_text = item["answer"]
        try:
            collection.add(
                documents=[q_text], metadatas=[{"answer": ans_text}], ids=[f"faq_{idx}"]
            )
        except Exception as e:
            st.error(f"Error adding FAQ '{q_text[:30]}...': {e}")

    return client, collection


# Initialize ChromaDB client and collection with persistent storage
if "chroma_client" not in st.session_state:
    # Only initialize if we're not in a testing environment
    if not os.getenv("TESTING"):
        st.session_state.chroma_client, st.session_state.faq_collection = init_chroma()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set page config
st.set_page_config(page_title="Thoughtful AI FAQ", page_icon="🤖", layout="wide")

# Display header
st.title("Thoughtful AI FAQ Assistant")
st.write("Ask me anything about Thoughtful AI's healthcare automation solutions!")

# Display existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input widget
user_input = st.chat_input("Ask a question about Thoughtful AI")
if user_input:
    # Display the user's question
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Retrieval Step 1: Exact match check
    query = user_input.strip().lower()
    answer_found = None
    for item in faq_data:
        if item["question"].lower() == query:
            answer_found = item["answer"]
            source = "faq"
            break

    # Retrieval Step 2: Similarity search if no exact match
    if answer_found is None:
        try:
            results = st.session_state.faq_collection.query(
                query_texts=[user_input], n_results=1
            )
        except Exception as e:
            st.error(f"Error during similarity search: {e}")
            results = None

        if results and results.get("metadatas") and results["metadatas"][0]:
            top_metadata = results["metadatas"][0][0]
            top_answer = top_metadata.get("answer")
            similarity_score = None
            if results.get("distances"):
                similarity_score = results["distances"][0][0]

            if top_answer and (similarity_score is None or similarity_score < 0.3):
                answer_found = top_answer
                source = "faq"

    # Retrieval Step 3: GPT fallback if no answer from knowledge base
    if answer_found is None:
        source = "gpt"
        try:
            # Create a placeholder for streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                # Stream the response
                stream = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant for Thoughtful AI, a company that provides AI-powered automation agents for healthcare processes. If you don't know the answer, say so politely.",
                        },
                        {"role": "user", "content": user_input},
                    ],
                    stream=True,
                )

                # Stream the response
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                # Final update without cursor
                message_placeholder.markdown(full_response)
                answer_found = full_response
                # Add source caption
                st.caption("Source: AI Assistant")

            # Add the GPT response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            answer_found = (
                "I'm sorry, I couldn't find an answer to that question at the moment."
            )
            st.error(f"OpenAI API error: {e}")
            # Add error response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": answer_found}
            )

    # Display the assistant's answer (for FAQ responses)
    elif answer_found and source == "faq":
        with st.chat_message("assistant"):
            st.markdown(answer_found)
            st.caption("Source: FAQ Knowledge Base")
        st.session_state.messages.append({"role": "assistant", "content": answer_found})
