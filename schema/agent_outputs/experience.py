from pydantic import BaseModel, Field
from typing import List

class Experience(BaseModel):
    job_title: str = Field(description="The job title of the applicant.")
    company: str = Field(description="The company where the applicant worked.")
    dates: str = Field(description="The dates of employment.")
    responsibilities: List[str] = Field(default=[], description="A list of responsibilities held in the position.")