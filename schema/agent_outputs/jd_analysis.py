from pydantic import BaseModel, Field
from typing import List
from schema.agent_outputs.experience import Experience

class JDAnalysis(BaseModel):
    job_summary: str = Field(description="A brief summary of the job description.")
    required_technical_skills: List[str] = Field(default=[], description="A list of required technical skills for the job.")
    preferred_technical_skills: List[str] = Field(default=[], description="A list of preferred technical skills for the job.")
    required_soft_skills: List[str] = Field(default=[], description="A list of the required soft skills for the job.")
    preferred_soft_skills: List[str] = Field(default=[], description="A list of the preferred soft skills for the job.")
    preferred_work_experiences: List[Experience] = Field(default=[], description="A list of preferred work experiences for the job.")