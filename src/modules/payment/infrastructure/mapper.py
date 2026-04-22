from src.db.base import mapper_registry
from src.modules.payment.domain.aggregate.model import Payment
from src.modules.payment.infrastructure.entity import PaymentEntity


def start_mapper():
    payment_table = PaymentEntity.__table__
    
    mapper_registry.map_imperatively(
        Payment,
        payment_table,
    )
