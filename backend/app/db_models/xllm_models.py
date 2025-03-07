from sqlmodel import SQLModel, Field, Session, create_engine, select, TIMESTAMP, text, Column
from typing import Optional, List, Dict
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB, DOUBLE_PRECISION

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
    log_timestamp: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"))
        )
    
class XLLMEmbeddings(SQLModel, table=True):
    __tablename__ = "xllm_embeddings"
    key: str = Field(primary_key=True, index=True)  # Unique identifier
    embeddings: Dict[str, float] = Field(sa_type=JSONB)  # JSONB column for embeddings
    
class XLLMSortedNgrams(SQLModel, table=True):
    __tablename__ = "xllm_sorted_ngrams"
    key: str = Field(primary_key=True, index=True)  # Unique identifier
    ngrams: str
    
class XLLMChunkDetails(SQLModel, table=True):
    __tablename__ = "xllm_chunk_details"
    chunk_id: str = Field(primary_key=True, index=True)  # Unique identifier
    content: Optional[Dict] = Field(sa_type=JSONB)
    size: int
    agents: Optional[str]
    index: Optional[str]