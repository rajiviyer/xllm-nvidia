from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from .docs_processing import get_docs
from .llm_processing import parse_docs

app = FastAPI()

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

@app.post("/api/parse_docs")
def parse_docs(parsed_text: Annotated[str, Depends(parse_docs)]):
    print("Successfully parsed docs")
    return parsed_text