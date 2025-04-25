from pydantic import BaseModel, Field


class CreateExchange(BaseModel):
    from_val: str = Field(min_length=1, max_length=20)
    to_val: str = Field(min_length=1, max_length=20)
    amount: int = Field()
