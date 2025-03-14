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
    # distill: bool
    # maxTokenCount: int
    # nresults: int
    
    # embeddingKeyMinSize: int
    # embeddingValuesMinSize: int
    # min_pmi: float
    # Customized_pmi: bool
    # minOutputListSize: int
    # nABmin: int
    # ContextMultitokenMinSize: int
    # maxTokenCount: int
    # ignoreList: str
    
    # bypassIgnoreList: int