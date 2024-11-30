import stripe  # type: ignore
from sqlalchemy.orm import Session
from ..model.schema import PaymentTransaction,PaymentRequest
import logging
from fastapi import HTTPException,Depends
from dotenv import load_dotenv # type: ignore
from typing import Annotated
from ..database.db import get_session
from ..database.db import get_session
import os

load_dotenv()

API_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = API_KEY
print(stripe.api_key)

async def call_payment_gateway(payment_request: PaymentRequest):
    try:
        payment = stripe.PaymentIntent.create(
            amount=int(payment_request.amount * 100),
            currency=payment_request.currency,
            payment_method_types=["card"],
            confirmation_method='manual', 
            confirm=True,
        )
        
        return {
            "status": payment['status'],
            "id": payment['id'],
            "charges": payment['charges']
        }
    except stripe.error.CardError as e:
#            # Handle payment gateway errors
            return {"status": "failed", "error": str(e)}
    except Exception as e:
            # General error handling for Stripe errors
            logging.error(f"Stripe error: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing payment gateway request.")
       


async def process_payments(payment_request: PaymentRequest, session:Annotated[Session,Depends(get_session)]):
    try:
        gateway_response= await call_payment_gateway(payment_request=payment_request)
        payment_status = 'completed' if gateway_response['status'] == 'succeeded' else 'failed'
        transaction = PaymentTransaction(
                user_id=payment_request.user_id,
                order_id=payment_request.order_id,
                amount=payment_request.amount,
                currency=payment_request.currency,
                payment_method=payment_request.payment_method,
                status=payment_status,
                transaction_reference=gateway_response.get('id', None),  # Stripe transaction ID
                payment_gateway_response=gateway_response.get('charges', {}).get('data', [{}])[0].get('receipt_url', None),
            )
        session.add(transaction)
        session.commit()
        return transaction
        
    except Exception as e:
            session.rollback()  
            logging.error(f"Error processing payment: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing payment: {str(e)}")
    






# class PaymentService:
#     def __init__(self):
#         stripe.api_key = "sk_test_51QQZOBK2Iih5e1AHdyJMnbljbW1PLWdkhyse3DMJj3eybpFqwCMmZfMRCZBCzwucVyciVhQqRZ1gSJY1lSNsnENP00We8JIwtk"  # Replace with your actual Stripe secret key
      
#     async def process_payments(self, payment_request: PaymentRequest, session: Session):
        
#         try:
#             gateway_response = await self.call_payment_gateway(payment_request)
#             payment_status = 'completed' if gateway_response['status'] == 'succeeded' else 'failed'
#             transaction = PaymentTransaction(
#                 user_id=payment_request.user_id,
#                 order_id=payment_request.order_id,
#                 amount=payment_request.amount,
#                 currency=payment_request.currency,
#                 payment_method=payment_request.payment_method,
#                 status=payment_status,
#                 transaction_reference=gateway_response.get('id', None),  # Stripe transaction ID
#                 payment_gateway_response=gateway_response.get('charges', {}).get('data', [{}])[0].get('receipt_url', None),
#             )
#             session.add(transaction)
#             session.commit()
#             return transaction
        
#         except Exception as e:
#             session.rollback()  
#             logging.error(f"Error processing payment: {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Error processing payment: {str(e)}")

#     async def call_payment_gateway(self, payment_request: PaymentRequest):
#         try:
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=int(payment_request.amount * 100),  # Convert to smallest currency unit (e.g., cents)
#                 currency=payment_request.currency,
#                 payment_method=payment_request.payment_method,  # Payment method ID from frontend
#                 confirmation_method='manual',  # Manual confirmation required
#                 confirm=True,  # Confirm immediately
#             )
#             return {
#                 "status": payment_intent['status'],
#                 "id": payment_intent['id'],
#                 "charges": payment_intent['charges']     #             }
#             }
#         except stripe.error.CardError as e:
#             # Handle payment gateway errors
#             return {"status": "failed", "error": str(e)}
#         except Exception as e:
#             # General error handling for Stripe errors
#             logging.error(f"Stripe error: {str(e)}")
#             raise HTTPException(status_code=500, detail="Error processing payment gateway request.")
