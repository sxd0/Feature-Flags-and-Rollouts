from pydantic import BaseModel, Field


class FlagCreate(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=512)


class FlagOut(BaseModel):
    id: int
    key: str
    description: str | None

    model_config = {"from_attributes": True}


class EnvCreate(BaseModel):
    name: str = Field(min_length=1, max_length=32)


class EnvOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class FlagStateUpsert(BaseModel):
    enabled: bool
    rollout_percentage: int = Field(ge=0, le=100)


class FlagStateOut(BaseModel):
    env: str
    enabled: bool
    rollout_percentage: int


class EvaluateResponse(BaseModel):
    env: str
    user_id: str
    flags: dict[str, bool]
