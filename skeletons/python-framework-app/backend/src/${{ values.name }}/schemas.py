"""What the API receives and answers."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models import ${{ values.Entity }}Status


class ${{ values.Entity }}In(BaseModel):
    name: str = Field(min_length=1, max_length=80, examples=["Rex"])
    category: str = Field(min_length=1, max_length=40, examples=["tools"])
    status: ${{ values.Entity }}Status = ${{ values.Entity }}Status.active
    start_date: date | None = None

    @field_validator("name", "category")
    @classmethod
    def trimmed(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("it cannot be blank")
        return value

    @field_validator("start_date")
    @classmethod
    def not_in_the_future(cls, value: date | None) -> date | None:
        if value and value > date.today():
            raise ValueError("it cannot be in the future")
        return value


class ${{ values.Entity }}Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    status: ${{ values.Entity }}Status
    start_date: date | None
    created_at: datetime
    created_by: str
