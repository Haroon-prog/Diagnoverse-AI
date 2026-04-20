from typing import TypedDict,Annotated,Optional,Any,List,Dict

class AgentState(TypedDict):
      # Input
    input_type: Optional[str]
    input_data: Optional[Any]
    file_name: Optional[str]
    
    # Extraction Agent
    extracted_text: Optional[str]
    cleaned_text: Optional[str]
    medications: List[dict]
    conditions: List[dict]
    lab_values: List[dict]
    rag_context: Optional[str]
    
    # Drug Checker Agent
    drug_interactions: List[Dict]
    side_effects: List[Dict]
    drug_warnings: List[Dict]
    
    # Query Generator Agent
    doctor_questions: List[str]
    
    # Summary Agent
    summary: Dict