from fastapi.testclient import TestClient
from payment_service.main import app 
from unittest.mock import patch


client = TestClient(app)


@patch('payment_service.paymentcrud.crud.stripe.PaymentIntent.create')  # Update the path as necessary
def test_process_payment(mock_stripe_create):
    # Define the mock response from Stripe's PaymentIntent.create
    mock_stripe_create.return_value = {
        'status': 'succeeded',
        'id': 'pi_12345',
        'charges': {'data': [{'receipt_url': 'https://example.com/receipt'}]}
    }
    
    # Define the test payload
    payment_request = {
        "user_id": 1,
        "order_id": 1234,
        "amount": 50.00,
        "currency": "usd",
        "payment_method": "pm_card_visa"
    }
    # Send a POST request to the /process-payment/ endpoint with the test payload
    response = client.post("/process-payment/", json=payment_request)
    
    # Assert the response status and body
    assert response.status_code == 200
    assert response.json() == {"status": "success", "transaction_id": "pi_12345"}




