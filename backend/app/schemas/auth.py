from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)

class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str

class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)

class RoadmapRequest(BaseModel):
    target_role: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)

class SavedJobRequest(BaseModel):
    job_id: int

class ApplicationRequest(BaseModel):
    job_id: int
    status: str = Field(default="saved", max_length=40)
    notes: str | None = None
    application_date: str | None = None

class ApplicationUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=40)
    notes: str | None = None
    application_date: str | None = None

class JourneyImportRequest(BaseModel):
    data: dict[str, str | None] = Field(default_factory=dict)
