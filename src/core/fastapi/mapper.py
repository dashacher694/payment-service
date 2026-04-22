from src.modules.outbox.infrastructure.mapper import start_mapper as outbox_mapper
from src.modules.payment.infrastructure.mapper import start_mapper as payment_mapper


def start_mapper():
    """Инициализация всех мапперов"""
    outbox_mapper()
    payment_mapper()
