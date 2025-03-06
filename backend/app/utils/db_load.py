from fastapi import Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..db.db_connector import get_session
from ..db_models.xllm_models import XLLMDictionary
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
        
        # Open the file as a stream
        records = []
        batch_size = 10000  # Process in chunks of 10K rows
        query = text("SELECT xllm_bulk_upsert_dictionary(:json_data::jsonb)")
        # query = """
        #     INSERT INTO XLLMDictionary (token, frequency)
        #     VALUES (:token, :frequencies)
        #     ON CONFLICT (token) DO UPDATE 
        #     SET frequency = EXCLUDED.frequency;
        # """        
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
