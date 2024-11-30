from fastapi import APIRouter,HTTPException,Depends
from ..database.db import get_session
from ..model.schema import PaymentRequest
from sqlmodel import Session
from ..paymentcrud.crud import process_payments


router = APIRouter()


@router.post("/process-payment/")
async def process_payment(payment_request:PaymentRequest, session: Session = Depends(get_session)):

    try:
        transaction = await process_payments(payment_request=payment_request,session=session)
        return {"status": "success", "transaction_id": transaction.transaction_reference}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the payment.")
    

