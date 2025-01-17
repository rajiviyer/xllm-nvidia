from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from .docs_processing import get_docs

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
    print("Successfully retrieved docs")
    return docs

