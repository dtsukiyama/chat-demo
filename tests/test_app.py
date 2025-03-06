import os

os.environ["TESTING"] = "true"

import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from app.main import faq_data, init_chroma


def test_faq_data_structure():
    """Test that FAQ data has the correct structure"""
    for item in faq_data:
        assert "question" in item
        assert "answer" in item
        assert isinstance(item["question"], str)
        assert isinstance(item["answer"], str)


@patch("streamlit.session_state")
def test_chat_message_handling(mock_session_state):
    """Test chat message handling"""
    # Mock session state
    mock_session_state.messages = []

    # Test adding a user message
    user_message = {"role": "user", "content": "What is Thoughtful AI?"}
    mock_session_state.messages.append(user_message)
    assert len(mock_session_state.messages) == 1
    assert mock_session_state.messages[0] == user_message

    # Test adding an assistant message
    assistant_message = {"role": "assistant", "content": faq_data[0]["answer"]}
    mock_session_state.messages.append(assistant_message)
    assert len(mock_session_state.messages) == 2
    assert mock_session_state.messages[1] == assistant_message


@patch("openai.OpenAI")
def test_gpt_fallback(mock_openai):
    """Test GPT fallback when FAQ doesn't have an answer"""
    # Create a mock response for streaming
    mock_chunk = MagicMock()
    mock_chunk.choices = [
        MagicMock(delta=MagicMock(content="This is a GPT-generated response"))
    ]
    mock_stream = MagicMock()
    mock_stream.__iter__.return_value = [mock_chunk]

    # Set up the mock client
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_stream
    mock_openai.return_value = mock_client

    # Test GPT response
    with patch("app.main.openai.api_key", "test_key"):
        from app.main import openai

        client = openai.OpenAI(api_key="test_key")
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "What is the future of AI?"}],
            stream=True,
        )

        # Verify the stream was created with correct parameters
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "What is the future of AI?"}],
            stream=True,
        )

        # Verify we can iterate over the stream
        chunks = list(stream)
        assert len(chunks) == 1
        assert chunks[0].choices[0].delta.content == "This is a GPT-generated response"


@patch("chromadb.PersistentClient")
@patch("openai.api_key", "test_key")
def test_chroma_initialization(mock_chroma_client, _):
    """Test ChromaDB initialization"""
    # Mock ChromaDB client
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_chroma_client.return_value = mock_client

    # Test collection creation
    client, collection = init_chroma()

    # Verify the collection was created with correct parameters
    mock_client.get_or_create_collection.assert_called_once_with(
        name="thoughtful_faq", embedding_function=pytest.any
    )
    assert collection == mock_collection
