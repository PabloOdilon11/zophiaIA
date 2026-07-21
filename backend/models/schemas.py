from typing import List, Optional
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    text: str

class AnalysisResult(BaseModel):
    report_type: str
    welcoming_summary: str
    signs: List[str]
    educational_info: str
    suggested_cares: List[str]
    when_to_seek_help: str
    sources: List[str]
    safety_notice: str
    risk_warning: bool

class DatasetStats(BaseModel):
    records: int
    categories_count: int
    missing_values: int
    average_length: float
    categories: dict
