from pydantic import BaseModel
from ..shared import IntString

class SellModel(BaseModel):
	item: IntString
	success: bool
	price: float
	seller_gets: float