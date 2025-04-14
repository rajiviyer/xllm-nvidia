import sys
import os

# Add the backend directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.response_generator_model import ResponseGenerator


def parse_docs_gemma(text, question) -> str:
    pipeline = ResponseGenerator(info_cards=text, user_question=question)
    response_generator = pipeline.chat()
    response = "".join(response_generator)  # Consume the generator
    print(f"Response: {response}")
    return response


if __name__ == "__main__":
    # Test the function with some sample data
    sample_text = "This is a sample text for testing."
    sample_question = "What is this text about?"
    parse_docs_gemma(sample_text, sample_question)
