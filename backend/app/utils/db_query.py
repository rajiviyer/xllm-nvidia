from fastapi import Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from ..db.db_connector import get_session
from ..db_models.xllm_models import XLLMDictionary, XLLMEmbeddings
from ..utils.types import getDocsFromDBParamsType
from typing import Dict, List, Optional, Annotated
import numpy as np
import json

def getDocsFromDB(params: getDocsFromDBParamsType, session: Session = None):
    """
    Get documents from the database.

    Args:
        params (getDocsFromDBParamsType): Parameters for the query.
        session (Session): The database session.

    Returns:
        List[Dict[str, float]]: A list of dictionaries containing document embeddings and metadata.
    """
    if session is None:
        session_gen = get_session()
        session = next(session_gen)
    
    try:            
        query = text("SELECT * from process_query(:json_data)")
        docs = session.execute(query, {"json_data": json.dumps(params)}).fetchall()
        return docs
    except Exception as e:
        print(f"Error in getDocsFromDB: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
        