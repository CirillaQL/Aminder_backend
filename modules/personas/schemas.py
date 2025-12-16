from pydantic import BaseModel, Field
from typing import List, Optional

class BigFiveProfileSchema(BaseModel):
    openness: float = Field(..., description="开放性 (0.0 - 1.0)")
    conscientiousness: float = Field(..., description="尽责性 (0.0 - 1.0)")
    extraversion: float = Field(..., description="外向性 (0.0 - 1.0)")
    agreeableness: float = Field(..., description="宜人性 (0.0 - 1.0)")
    neuroticism: float = Field(..., description="神经质 (0.0 - 1.0)")
    traits: List[str] = Field(default_factory=list, description="AI 生成的特征标签")

class PersonaCreateRequest(BaseModel):
    name: str = Field(..., description="角色姓名")
    gender: str = Field(..., description="角色性别")
    description: str = Field(..., description="角色描述")
    if_original: bool = Field(False, description="是否原创角色")

class PersonaResponse(BaseModel):
    name: str
    gender: str
    personality: BigFiveProfileSchema
