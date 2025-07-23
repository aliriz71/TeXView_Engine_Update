from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TexviewPDF(BaseModel):
    id: str = Field(..., alias="_id")
    filename: str
    text: str
    latex: Optional[str] = None
    uploaded_at: datetime