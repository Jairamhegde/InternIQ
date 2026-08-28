from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# -------------BASE MODELS------------------------

class Basemodel(BaseModel):
    pass

class OverviewInsightsModel(Basemodel):
    year: int = Field(default_factory=lambda: datetime.now().year)
    tile_data: Dict[str, Any]
    field: str = 'all'

class RolesPostingsModel(Basemodel):
    roles: List[str]

class CommonSkillModal(Basemodel):
    roles: List[str]

class ComparitiveInsightsModal(Basemodel):
    role_frequency: List[Any]
    common_skill: List[Any]

class JobpostingModel(BaseModel):
    year: int
    field: str

class TopCompanyModel(BaseModel):
    year: int
    field: str

