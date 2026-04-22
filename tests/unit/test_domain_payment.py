import pytest
from decimal import Decimal
from datetime import datetime

from src.modules.payment.domain.aggregate.model import Payment
from src.modules.utils.enums import PaymentStatus, Currency


@pytest.mark.unit
class TestPaymentDomain:
    """Unit tests for Payment domain model"""
    
    def test_create_payment(self):
        """Test payment creation with valid data"""
        payment = Payment(
            amount=Decimal("1000.50"),
            currency=Currency.RUB,
            description="Test payment",
            meta={"order_id": "123"},
            idempotency_key="test-key-123",
            webhook_url="https://webhook.site/test",
            status=PaymentStatus.pending,
        )
        
        assert payment.amount == Decimal("1000.50")
        assert payment.currency == Currency.RUB
        assert payment.status == PaymentStatus.pending
        assert payment.description == "Test payment"
        assert payment.meta == {"order_id": "123"}
        assert payment.idempotency_key == "test-key-123"
        assert payment.webhook_url == "https://webhook.site/test"
        assert payment.processed_at is None
    
    def test_payment_status_transition_to_succeeded(self):
        """Test payment status transition to succeeded"""
        payment = Payment(
            amount=Decimal("100.00"),
            currency=Currency.USD,
            description="Test",
            meta={},
            idempotency_key="key-1",
            webhook_url="https://test.com",
            status=PaymentStatus.pending,
        )
        
        payment.status = PaymentStatus.succeeded
        payment.processed_at = datetime.utcnow()
        
        assert payment.status == PaymentStatus.succeeded
        assert payment.processed_at is not None
    
    def test_payment_status_transition_to_failed(self):
        """Test payment status transition to failed"""
        payment = Payment(
            amount=Decimal("100.00"),
            currency=Currency.EUR,
            description="Test",
            meta={},
            idempotency_key="key-2",
            webhook_url="https://test.com",
            status=PaymentStatus.pending,
        )
        
        payment.status = PaymentStatus.failed
        payment.processed_at = datetime.utcnow()
        
        assert payment.status == PaymentStatus.failed
        assert payment.processed_at is not None
