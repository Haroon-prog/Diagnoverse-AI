from pydantic import BaseModel, Field
from typing import List, Optional


class Medication(BaseModel):
    name: str = Field(description="Name of the medicine")
    description: Optional[str] = Field(
        default=None,
        description="What the medicine is used for"
    )


class Condition(BaseModel):
    name: str = Field(description="Name of the condition or disease")
    description: Optional[str] = Field(
        default=None,
        description="Short explanation of the condition"
    )


class LabValue(BaseModel):
    name: str = Field(description="Name of the lab test")
    value: Optional[str] = Field(
        default=None,
        description="Value of the lab test if present"
    )
    description: Optional[str] = Field(
        default=None,
        description="What this lab test indicates"
    )


class MedicalEntities(BaseModel):
    medications: List[Medication]
    conditions: List[Condition]
    lab_values: List[LabValue]