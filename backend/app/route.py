from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from .db.db_connector import get_session, create_table
from contextlib import asynccontextmanager
from .docs_processing import get_docs, get_docs_from_db
from .llm_processing import parse_docs
from .utils.db_load import (upload_dictionary_file, upload_embeddings_file, upload_sorted_ngrams_file, 
                            upload_chunks_file, upload_chunks_contents_file, upload_chunks_agents_file,
                            upload_chunks_index_file, upload_hash_ids_file, upload_hash_unstem_file,
                            upload_hash_stem_file, upload_stop_words_file)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating Tables..")
    create_table()
    yield

app = FastAPI(lifespan=lifespan)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Welcome!"

# @app.get("/")
# def home():
#     return f"""
#             Dictionary size: {len(backendTables['dictionary'])}\n
#             Hash pairs size: {len(backendTables['hash_pairs'])}\n
#             Ctokens size: {len(backendTables['ctokens'])}
# #         """

@app.post("/api/docs")
def get_docs(docs: Annotated[dict, Depends(get_docs)]):
    if docs:
        print("Successfully retrieved docs")
        raw_content = docs["complete_content"]
        processed_content = parse_docs(raw_content)
        docs["complete_content"] = processed_content
    return docs

@app.post("/api/docs_from_db")
def get_docs_from_db(docs: Annotated[dict, Depends(get_docs_from_db)]):
    if docs:
        print("Successfully retrieved docs")
    return docs

@app.post("/api/parse_docs")
def parse_docs(parsed_text: Annotated[str, Depends(parse_docs)]):
    print("Successfully parsed docs")
    return parsed_text

@app.post("/api/dictionary/upload")
async def upload_dictionary_file(message: str = Depends(upload_dictionary_file)):
    return {"message": message}

@app.post("/api/embeddings/upload")
async def upload_embeddings_file(message: str = Depends(upload_embeddings_file)):
    return {"message": message}

@app.post("/api/sorted_ngrams/upload")
async def upload_sorted_ngrams_file(message: str = Depends(upload_sorted_ngrams_file)):
    return {"message": message}

@app.post("/api/chunks/upload")
async def upload_chunks_file(message: str = Depends(upload_chunks_file)):
    return {"message": message}

@app.post("/api/chunks_contents/upload")
async def upload_chunks_contents_file(message: str = Depends(upload_chunks_contents_file)):
    return {"message": message}

@app.post("/api/chunks_agents/upload")
async def upload_chunks_agents_file(message: str = Depends(upload_chunks_agents_file)):
    return {"message": message}

@app.post("/api/chunks_index/upload")
async def upload_chunks_index_file(message: str = Depends(upload_chunks_index_file)):
    return {"message": message}

@app.post("/api/hash_ids/upload")
async def upload_hash_ids_file(message: str = Depends(upload_hash_ids_file)):
    return {"message": message}

@app.post("/api/hash_unstem/upload")
async def upload_hash_unstem_file(message: str = Depends(upload_hash_unstem_file)):
    return {"message": message}

@app.post("/api/hash_stem/upload")
async def upload_hash_stem_file(message: str = Depends(upload_hash_stem_file)):
    return {"message": message}

@app.post("/api/stop_words/upload")
async def upload_stop_words_file(message: str = Depends(upload_stop_words_file)):
    return {"message": message}