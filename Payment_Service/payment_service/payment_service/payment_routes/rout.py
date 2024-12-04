from fastapi import APIRouter, HTTPException, Depends
from ..database.db import get_session
from ..model.schema import PaymentRequest, PaymentResponse
from sqlmodel import Session
from ..paymentcrud.crud import process_payments
import logging
from stripe.error import StripeError

# Configure logging
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/process-payment/", response_model=PaymentResponse)
def process_payment(payment_request: PaymentRequest, session: Session = Depends(get_session)):
    """
    Process a payment request using Stripe payment gateway.

    Args:
        payment_request (PaymentRequest): The payment details.
        session (Session): Database session dependency.

    Returns:
        PaymentResponse: The status and transaction details of the payment.
    """
    try:
        transaction = process_payments(payment_request=payment_request, session=session)
        return {
            "status": "success",
            "transaction_id": transaction.transaction_id,
            "transaction_reference": transaction.transaction_reference,
            "amount": transaction.amount,
            "payment_method": transaction.payment_method,
            "payment_gateway_response": transaction.payment_gateway_response,
            "created_at": transaction.created_at,
            "processed_at": transaction.processed_at
        }
    except StripeError as e:
        logging.error(f"Stripe error: {e.user_message}")
        raise HTTPException(status_code=400, detail=e.user_message)
    except HTTPException as e:
        logging.error(f"HTTPException: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the payment.")
