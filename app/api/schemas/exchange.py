from pydantic import BaseModel, Field


class CreateExchange(BaseModel):
    text: str = Field(min_length=1, max_length=300)
