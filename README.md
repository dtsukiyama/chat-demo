# Thoughtful AI FAQ Assistant

A Streamlit-based chat application that provides intelligent responses about Thoughtful AI's healthcare automation solutions. The application uses a combination of predefined FAQs, semantic search with ChromaDB, and GPT-3.5 for comprehensive question answering.

## Features

- Interactive chat interface for asking questions about Thoughtful AI
- Predefined FAQ knowledge base with common questions and answers
- Semantic search using ChromaDB and OpenAI embeddings
- GPT-3.5 fallback for questions not covered in the FAQ
- Persistent chat history during the session
- Source attribution for answers (FAQ vs. AI-generated)
- Pre-commit hooks for code quality (Black formatting and linting)

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Docker (optional, for containerized deployment)
- Node.js and npm (for Lefthook installation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chat-demo.git
cd chat-demo
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

5. Set up pre-commit hooks:
   ```bash
   ./scripts/setup_hooks.sh
   ```
   This will:
   - Install Lefthook if not already installed
   - Configure Git hooks for pre-commit checks
   - Set up Black formatting and linting

## Usage

1. Run the Streamlit app:
```bash
streamlit run app/main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Start asking questions about Thoughtful AI's products and services!

## Docker Deployment

Build and run using Docker Compose:

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8501`

## Development

### Code Quality

This project uses pre-commit hooks to ensure code quality:

- **Black**: Code formatting and linting

The hooks run automatically when you commit changes. If you need to skip the hooks (not recommended), you can use:
```bash
git commit -m "your message" --no-verify
```

### Manual Code Quality Checks

You can also run the checks manually:

```bash
# Format and lint code
black --check app/ tests/
```

## Environment Variables

The following environment variables are required:

- `OPENAI_API_KEY`: Your OpenAI API key for accessing the GPT-3.5 API

For local development:
1. Copy `.env.example` to `.env`
2. Add your API key to the `.env` file
3. Never commit the `.env` file to version control

## How It Works

1. **Exact Match**: The system first checks for exact matches against predefined FAQs
2. **Semantic Search**: If no exact match is found, it uses ChromaDB with OpenAI embeddings to find similar questions
3. **GPT Fallback**: If no relevant FAQ is found, it uses GPT-3.5 to generate an appropriate response

## License

MIT License - feel free to use this project for your own purposes.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request