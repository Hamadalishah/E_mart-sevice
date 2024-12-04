import stripe  # type: ignore
from sqlalchemy.orm import Session
from ..model.schema import PaymentTransaction,PaymentRequest
import logging
from fastapi import HTTPException,Depends
from dotenv import load_dotenv # type: ignore
from typing import Annotated
from datetime import datetime
import uuid
from ..database.db import get_session
import os
import logging


logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = "sk_test_51QQZPhJ17hHGYtqJkbIbT8aXwFOpPujcjrP0L3DKoswclPcqwWtOLKhXdnJYTbpDiBgbNVxdcVkwn6KGGAFgXulA00Wu4xNBh4"
print(API_KEY)
stripe.api_key = API_KEY
print(stripe.api_key)


def call_payment_gateway(payment_request: PaymentRequest) -> dict:
    try:
        # Generate a unique idempotency key for each payment attempt
        idempotency_key = str(uuid.uuid4())
        
        if payment_request.payment_method:
            # Use existing PaymentMethod ID
            payment_method = payment_request.payment_method
        elif payment_request.card_number and payment_request.exp_month and payment_request.exp_year and payment_request.cvc:
            # Create a new PaymentMethod using card details
            payment_method_obj = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": payment_request.card_number,
                    "exp_month": payment_request.exp_month,
                    "exp_year": payment_request.exp_year,
                    "cvc": payment_request.cvc,
                },
            )
            payment_method = payment_method_obj.id
        else:
            raise HTTPException(status_code=400, detail="Either payment_method ID or complete card details must be provided.")
        
        # Create PaymentIntent
        payment = stripe.PaymentIntent.create(
            amount=int(payment_request.amount * 100),  # Convert to cents
            currency=payment_request.currency,
            payment_method_types=["card"],
            payment_method=payment_method,
            confirmation_method='automatic',  # Ensure automatic confirmation
            confirm=True,
            idempotency_key=idempotency_key,  # Unique per transaction
        )
        
        logging.info(f"Stripe PaymentIntent created: {payment}")
        
        # Retrieve the latest_charge ID
        latest_charge_id = payment.get('latest_charge')
        if latest_charge_id:
            # Retrieve the Charge object using the Charge ID
            charge = stripe.Charge.retrieve(latest_charge_id)
            receipt_url = charge.get('receipt_url')
        else:
            charge = None
            receipt_url = None
        
        return {
            "status": payment.get('status'),
            "id": payment.get('id'),
            "receipt_url": receipt_url
        }
    except stripe.error.CardError as e:
        # Handle payment gateway errors
        logging.error(f"Stripe CardError: {str(e)}")
        return {"status": "failed", "error": str(e)}
    except stripe.error.RateLimitError as e:
        logging.error(f"Stripe RateLimitError: {str(e)}")
        return {"status": "failed", "error": "Rate limit exceeded. Please try again later."}
    except stripe.error.InvalidRequestError as e:
        logging.error(f"Stripe InvalidRequestError: {str(e)}")
        return {"status": "failed", "error": "Invalid parameters. Please check your request."}
    except Exception as e:
        # General error handling for Stripe errors
        logging.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing payment gateway request.")

    
    
def process_payments(payment_request: PaymentRequest, session: Session) -> PaymentTransaction:
    try:
        gateway_response = call_payment_gateway(payment_request=payment_request)
        logging.info(f"Gateway response: {gateway_response}")

        payment_status = 'completed' if gateway_response.get('status') == 'succeeded' else 'failed'
        
        if payment_status == 'completed':
            receipt_url = gateway_response.get('receipt_url')
        else:
            receipt_url = None
        
        transaction = PaymentTransaction(
            user_id=payment_request.user_id,
            order_id=payment_request.order_id,
            amount=payment_request.amount,
            currency=payment_request.currency,
            payment_method=payment_request.payment_method,
            status=payment_status,
            transaction_reference=gateway_response.get('id'),  # PaymentIntent ID
            payment_gateway_response=receipt_url,
            processed_at=datetime.utcnow() if payment_status == 'completed' else None
        )
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception as e:
        session.rollback()
        logging.error(f"Error processing payment for user_id {payment_request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing payment: {str(e)}")
