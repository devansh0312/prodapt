from pydantic import BaseModel, Field


class OperatorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    circle: str = Field(min_length=2, max_length=100)


class OperatorResponse(OperatorCreate):
    id: str
