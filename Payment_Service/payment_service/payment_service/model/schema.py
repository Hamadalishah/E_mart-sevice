from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentTransaction(SQLModel, table=True):
    transaction_id: Optional[int] = Field(default=None, primary_key=True)  # Unique transaction ID
    user_id: int  # User ID from the User service (foreign key)
    order_id: int  # Reference to order, optional depending on your workflow
    amount: float  # Total payment amount
    currency: str  # Payment currency (USD, EUR, INR)
    payment_method: str  # Payment method (credit_card, paypal, etc.)
    status: str  # Payment status ('pending', 'completed', 'failed', 'refunded', etc.)
    transaction_reference: Optional[str] = None  # Reference to external gateway
    payment_gateway_response: Optional[str] = None  # Response from payment gateway
    created_at: datetime = Field(default=datetime.utcnow())  # Payment initiation time
    updated_at: Optional[datetime] = Field(default=None)  # Last updated time
    processed_at: Optional[datetime] = None  # Timestamp for when the payment was processed


class PaymentMethod(SQLModel, table=True):
    method_id: Optional[int] = Field(default=None, primary_key=True)  # Unique ID for each payment method
    name: str  # Payment method name (credit_card, paypal, etc.)
    description: Optional[str]  # Description for the payment method
    is_active: bool = True  # Whether the payment method is active or not
    created_at: datetime = Field(default=datetime.utcnow())  # Timestamp of method creation
    updated_at: Optional[datetime] = None  # Timestamp of last update



class RefundRequest(SQLModel, table=True):
    refund_id: Optional[int] = Field(default=None, primary_key=True)  # Unique refund ID
    transaction_id: int  # Reference to the PaymentTransaction
    refund_amount: float  # Refund amount
    refund_status: str  # Refund status ('pending', 'completed', 'failed')
    reason: Optional[str]  # Reason for the refund (optional)
    created_at: datetime = Field(default=datetime.utcnow())  # Timestamp of refund initiation
    updated_at: Optional[datetime] = None  # Timestamp of last update





class PaymentRequest(BaseModel):
    user_id: int  # User ID initiating the payment
    order_id: int  # ID of the order being paid for
    amount: float  # Total payment amount
    currency: str = 'USD'  # Payment currency
    payment_method: str  # Chosen payment method (e.g., 'credit_card', 'paypal')
    transaction_reference: Optional[str] = None  # Optional: Reference from external payment gateway


class PaymentResponse(BaseModel):
    transaction_id: int  # Unique transaction ID
    status: str  # Payment status ('completed', 'failed', etc.)
    amount: float  # Amount processed
    payment_method: str  # Method used for the payment
    payment_gateway_response: Optional[str] = None  # Response from payment gateway (optional)
    transaction_reference: Optional[str] = None  # Reference from the payment gateway
    created_at: datetime  # Payment initiation timestamp
    processed_at: Optional[datetime] = None  # Payment processing timestamp
