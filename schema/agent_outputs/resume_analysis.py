from pydantic import BaseModel, Field
from typing import List
from schema.agent_outputs.experience import Experience

class ResumeAnalysis(BaseModel):
    profile_summary: str = Field(description="A brief summary of the applicant's profile.")
    technical_skills: List[str] = Field(default=[], description="A list of technical skills possessed by the applicant.")
    soft_skills: List[str] = Field(default=[], description="A list of the applicant's soft skills.")
    work_experiences: List[Experience] = Field(default=[], description="A list of work experiences held by the applicant.")