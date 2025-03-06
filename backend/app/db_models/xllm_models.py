from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from datetime import datetime

class XLLMDictionary(SQLModel, table=True):
    __tablename__ = "xllm_dictionary"
    token: str = Field(primary_key=True, index=True)  # Unique key
    frequency: float
    
    
class XLLMLoadRunErrorLog(SQLModel, table=True):
    __tablename__ = "xllm_load_run_error_log"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    table_name: str
    error_message: str
    record_text: str
    log_timestamp: datetime