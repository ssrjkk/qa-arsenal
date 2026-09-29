from typing import List, Optional

from models.base_model import БазовыйМодель


class AreaModel(БазовыйМодель):
    id: str
    name: str
    parent_id: Optional[str] = None
    areas: List["AreaModel"] = []
    url: Optional[str] = None


AreaModel.model_rebuild()
