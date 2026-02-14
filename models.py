from typing import Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
  id: Optional[int] = None
  name: str
  description: str
  price: float
  stock: int = Field(alias="quantity")

  model_config = {
    "from_attributes": True,
    "populate_by_name": True,
    "by_alias": True
  }
