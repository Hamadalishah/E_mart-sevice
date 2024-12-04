from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field as PydanticField

class PaymentTransaction(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    order_id: str  # Ensure this is string type
    amount: float
    currency: str
    payment_method: str
    status: str
    transaction_reference: Optional[str] = None
    payment_gateway_response: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    processed_at: Optional[datetime] = None

class PaymentRequest(BaseModel):
    user_id: int
    order_id: str
    amount: float = PydanticField(..., gt=0)
    currency: str = 'USD'
    payment_method: Optional[str] = None  # PaymentMethod ID
    card_number: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    cvc: Optional[str] = None
    transaction_reference: Optional[str] = None

class PaymentResponse(BaseModel):
    status: str
    transaction_id: int
    transaction_reference: Optional[str] = None
    amount: float
    payment_method: str
    payment_gateway_response: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
