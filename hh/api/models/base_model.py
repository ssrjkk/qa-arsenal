from pydantic import BaseModel


class БазовыйМодель(BaseModel):
    model_config = {"extra": "ignore", "populate_by_name": True}
