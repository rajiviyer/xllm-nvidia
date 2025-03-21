from fastapi import Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..db.db_connector import get_session
from .types import getDocsFromDBParamsType
from ..db_models.xllm_models import XLLMDictionary, XLLMEmbeddings
from typing import Dict, List, Optional
import numpy as np
import json
# from app.schemas import GraphRequest
# from app.services.graph_service import get_graph_data

DBSession: Session = Depends(get_session)

# router = APIRouter()

async def upload_dictionary_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a dictionary file to the database.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10000  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_dictionary(:json_data)")
       
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                token = parts[0]
                frequency = float(parts[1])
                records.append({"token": token, "frequency": frequency})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add dictionary data into the database"


async def upload_embeddings_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a dictionary file to the database.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
        
    Data File Format:
    'investor'  {'presentation': 0.09667364890456637,'investor~presentation': 0.21616885058355848,'presentation~investor~presentation': 0.21616885058355848,'q2~fy24': 0.028507503806241983
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_embeddings(:json_data)")
      
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                key = parts[0]
                embeddings = eval(parts[1])
                records.append({"key": key, "embeddings": embeddings})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add dictionary data into the database"
    
async def upload_sorted_ngrams_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a key and list of ngrams.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
        
    Data File Format:
    fy24~q2	('q2~fy24', 'fy24~q2')
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_sorted_ngrams(:json_data)")
      
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                key = parts[0]
                ngrams = ", ".join(eval(parts[1]))
                records.append({"key": key, "ngrams": ngrams})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add dictionary data into the database" 
    
async def upload_chunks_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a chunk id and its size.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
        
    Data File Format:
    B714X1	194
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_chunks(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                key = parts[0]
                size = int(parts[1])
                records.append({"chunk_id": key, "size": size})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")

async def upload_chunks_contents_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads contents related to a chunk

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
        
    Data File Format:
    B0X0	{'title_text': 'Investor Presentation Q2 FY24', 'description_text': 'Investor Presentation Q2 FY24', 'type': 'Title', 'doc_ID': 0, 'pn': 0, 'block_ID': 0, 'item_ID': -1, 'sub_ID': -1, 'fs': 88.0, 'fc': 16777215, 'ft': 'NVIDIASans-Bold'}      
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_update_chunks_contents(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                chunk_id = parts[0]
                content = eval(parts[1])
                records.append({"chunk_id": chunk_id, "content": content})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and chunks content data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add chunks content into the database"    
    
async def upload_chunks_agents_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads agents related to a chunk

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
        
    Data File Format:
    B2X0	('Income', 'Tax', 'Cash', 'Products', 'Data', 'Accelerated Computing', 'Data Center', 'Non-GAAP')
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_update_chunks_agents(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                chunk_id = parts[0]
                agents = ", ".join(eval(parts[1]))
                records.append({"chunk_id": chunk_id, "agents": agents})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and chunks agents data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add chunks agents into the database"
    
async def upload_chunks_index_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads index related to a chunk

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
        
    Data File Format:
    B54X0	(0, 7)
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_update_chunks_index(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                chunk_id = parts[0]
                # index = ", ".join(eval(parts[1]))
                index = parts[1]
                print(f"index: {index}")
                records.append({"chunk_id": chunk_id, "index": index})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and chunks index data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add chunks index into the database"
    
async def upload_hash_ids_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a dictionary file to the database.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_hash_ids(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                key = parts[0]
                hashes = eval(parts[1])
                records.append({"key": key, "hashes": hashes})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and hash ids data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add hash ids into the database"
    
    
async def upload_hash_unstem_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a dictionary file to the database.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_hash_unstem(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                stem = parts[0]
                keywords = ", ".join(eval(parts[1]))
                records.append({"stem": stem, "keywords": keywords})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and hash unstem data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add hash unstem into the database"
    
async def upload_hash_stem_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a dictionary file to the database.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_hash_stem(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) == 2:
                keyword = parts[0]
                stem = parts[1]
                records.append({"keyword": keyword, "stem": stem})
            
            if len(records) >= batch_size:
                json_data = json.dumps(records)
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and hash stem data inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add hash stem into the database"
    
async def upload_stop_words_file(file: UploadFile = File(...), session: DBSession = Depends(get_session)):
    """
    Uploads a dictionary file to the database.

    Args:
        file (UploadFile): The dictionary file to upload.
        session (Session): The database session.

    Returns:
        str: A message indicating the success or failure of the upload.
    """
    try:
        
        # Read file as text (entire content)
        contents = await file.read()        
        
        records = []
        batch_size = 10001  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_insert_stop_words(:json_data)")
        for line in contents.decode("latin1").strip().split("\n"):
            records.append(line)
            
            if len(records) >= batch_size:
                json_data = json.dumps(records) 
                session.execute(query, {"json_data": json_data})
                records = []

        if records:
            print(f"sample record: {records[0]}") 
            json_data = json.dumps(records)
            session.execute(query, {"json_data": json_data})
        
        session.commit()        
        
        return {"message": "Success: File uploaded and stop words inserted into database."}
    except Exception as e:
        print(f"Exception: {str(e)}")
        return f"Error: Failed to add stop words into the database"   