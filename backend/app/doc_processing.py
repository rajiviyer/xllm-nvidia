import sys
import os
import time
import logging
import functools
from datetime import datetime

# Set up logger
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.types import frontendParamsType, UserQuery
from app.utils.params import defaultFrontendParams
from typing import Optional, List, Dict, Any, Generator, Callable, Union, Tuple
from app.settings import settings

from app.utils.db_query import getDocsFromDB, getEmbeddingsFromDB
from app.llm_processing import parse_docs_gemma

from nltk.stem import PorterStemmer
from collections import defaultdict


# Define a standalone decorator for timing
def time_function(func):
    """
    Decorator to time the execution of functions

    Args:
        func (Callable): Function to time

    Returns:
        Callable: Wrapped function with timing
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(
            f"Function '{func.__name__}' executed in {execution_time:.4f} seconds"
        )
        return result

    return wrapper


class DocumentProcessor:
    def __init__(self):
        """
        Initialize the DocumentProcessor class with a stemmer
        """
        self.stemmer = PorterStemmer()

    @time_function
    def preprocess_query(self, query: str) -> Dict[str, Any]:
        """
        Preprocess the query string

        Args:
            query (str): The query string to preprocess

        Returns:
            Dict[str, Any]: Processed query parameters
        """
        query_text = (
            query.replace("?", " ")
            .replace("(", " ")
            .replace(")", " ")
            .replace(".", " ")
        )
        query_text = query_text.replace("'", "").replace("\\s", "")
        query_text = query_text.split(" ")

        query_text = [word.lower() for word in query_text if word]
        stemmed_text = [self.stemmer.stem(word) for word in query_text]
        logger.debug(f"stemmed_text: {stemmed_text}")

        return {
            "query_text": query_text,
            "stemmed_text": stemmed_text,
        }

    @time_function
    def get_docs_from_db(self, form_params: frontendParamsType) -> Dict[str, Any]:
        """
        Get docs from database

        Args:
            form_params (frontendParamsType): User Input Data from Frontend

        Returns:
            Dict[str, Any]: Dictionary of List of Embeddings & Docs
        """
        logger.debug(f"form_params: {form_params}")
        use_stem = form_params["useStem"]
        beta = form_params["beta"]
        query = form_params["queryText"]
        distill = form_params["distill"]
        max_token_count = form_params["maxTokenCount"]
        nresults = form_params["nresults"]
        logger.debug(f"use_stem: {use_stem}")
        logger.debug(f"beta: {beta}")
        logger.debug(f"query: {query}")
        logger.debug(f"distill: {distill}")
        logger.debug(f"max_token_count: {max_token_count}")
        logger.debug(f"nresults: {nresults}")

        # Get processed query parameters
        processed_query = self.preprocess_query(query)
        query_text = processed_query["query_text"]
        stemmed_text = processed_query["stemmed_text"]

        query_params = {
            "use_stem": use_stem,
            "beta": beta,
            "query_text": query_text,
            "stemmed_text": stemmed_text,
            "distill": distill,
            "max_token_count": max_token_count,
        }

        try:
            # Step 1: Get docs from DB
            start_time = time.time()
            docs_from_db = getDocsFromDB(query_params)
            end_time = time.time()
            logger.debug(
                f"getDocsFromDB executed in {end_time - start_time:.4f} seconds"
            )

            docs = [
                {
                    "id": row[0],
                    "content": row[1],
                    "size": row[2],
                    "agents": row[3],
                    "rank": row[4],
                    "hash_id": "",
                }
                for row in docs_from_db
            ]

            # Step 2: Get embeddings from DB
            start_time = time.time()
            embeddings_from_db = getEmbeddingsFromDB(query_params)
            end_time = time.time()
            logger.debug(
                f"getEmbeddingsFromDB executed in {end_time - start_time:.4f} seconds"
            )

            doc_embeddings = [
                {"word": row[0], "embedding": row[1], "pmi": row[2]}
                for row in embeddings_from_db
            ]


            return {
                "embeddings": doc_embeddings,
                "docs": docs
            }
        except Exception as e:
            logger.error(f"Error in get_docs_from_db: {str(e)}", exc_info=True)
            # Return empty results when there's an error
            return {
                "embeddings": [],
                "docs": []
            }

    @time_function
    def get_llm_response(self, user_question: str) -> Generator[str, None, None]:
        """
        Get LLM Response

        Args:
            user_question (str): User Question

        Returns:
            Generator[str, None, None]: Stream of LLM Response
        """
        form_params = defaultFrontendParams
        form_params["queryText"] = user_question
        logger.debug(f"form_params: {form_params}")
        use_stem = form_params["useStem"]
        beta = form_params["beta"]
        query = user_question
        distill = form_params["distill"]
        max_token_count = form_params["maxTokenCount"]
        nresults = form_params["nresults"]

        try:
            # Get processed query parameters
            processed_query = self.preprocess_query(query)
            query_text = processed_query["query_text"]
            stemmed_text = processed_query["stemmed_text"]

            query_params = {
                "use_stem": use_stem,
                "beta": beta,
                "query_text": query_text,
                "stemmed_text": stemmed_text,
                "distill": distill,
                "max_token_count": max_token_count,
            }

            # Step 1: Get docs from DB
            start_time = time.time()
            docs_from_db = getDocsFromDB(query_params)
            end_time = time.time()
            logger.debug(
                f"getDocsFromDB executed in {end_time - start_time:.4f} seconds"
            )

            docs = [
                {
                    "id": row[0],
                    "content": row[1],
                    "size": row[2],
                    "agents": row[3],
                    "rank": row[4],
                    "hash_id": "",
                }
                for row in docs_from_db
            ]

            # Step 2: Get embeddings from DB
            start_time = time.time()
            embeddings_from_db = getEmbeddingsFromDB(query_params)
            end_time = time.time()
            logger.debug(
                f"getEmbeddingsFromDB executed in {end_time - start_time:.4f} seconds"
            )

            # Step 3: Generate LLM response
            logger.debug("Generating User Friendly Result")
            complete_raw_content = " ".join(
                [doc["content"]["description_text"] for doc in docs[:7]]
            )

            # Process and yield results
            start_overall = time.time()
            token_count = 0

            response = parse_docs_gemma(complete_raw_content, user_question)

            # Handle both string and generator cases
            if isinstance(response, str):
                # If string was returned directly, yield it as a single chunk
                token_count = len(response.split())
                current_time = time.time()
                elapsed = current_time - start_overall
                logger.debug(
                    f"Generated {token_count} tokens in {elapsed:.4f} seconds ({token_count/elapsed:.2f} tokens/sec)"
                )
                yield response
            else:
                # Iterate through generator
                for content in response:
                    token_count += len(content.split())
                    current_time = time.time()
                    elapsed = current_time - start_overall
                    logger.debug(
                        f"Generated {token_count} tokens in {elapsed:.4f} seconds ({token_count/elapsed:.2f} tokens/sec)"
                    )
                    yield content
        except Exception as e:
            logger.error(f"Error in get_llm_response: {str(e)}", exc_info=True)
            yield f"Error occurred while processing your request: {str(e)}"

    @time_function
    def test_gemma_parsing(self, test_text: str, test_question: str) -> str:
        """
        Test the Gemma parsing functionality

        Args:
            test_text (str): Test document text
            test_question (str): Test question

        Returns:
            str: Parsed result
        """
        try:
            start_time = time.time()
            result = parse_docs_gemma(test_text, test_question)
            end_time = time.time()
            logger.debug(
                f"parse_docs_gemma test executed in {end_time - start_time:.4f} seconds"
            )

            # Handle generator case
            if not isinstance(result, str):
                # Collect all chunks into a single string
                result_chunks = []
                for chunk in result:
                    result_chunks.append(chunk)
                result = " ".join(result_chunks)

            return result
        except Exception as e:
            logger.error(f"Error in test_gemma_parsing: {str(e)}", exc_info=True)
            return f"Error occurred: {str(e)}"


