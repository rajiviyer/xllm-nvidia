from typing_extensions import TypedDict

class frontendParamsType(TypedDict):
    useStem: bool
    beta: float
    queryText: str
    distill: bool
    maxTokenCount: int
    nresults: int
    
class getDocsFromDBParamsType(TypedDict):
    use_stem: bool
    beta: float
    query_text: str
    stemmed_text: list[str]