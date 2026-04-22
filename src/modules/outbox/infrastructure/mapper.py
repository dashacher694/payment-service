from src.db.base import mapper_registry
from src.modules.outbox.domain.aggregate.model import Outbox
from src.modules.outbox.infrastructure.entity import OutboxEntity


def start_mapper():
    outbox_table = OutboxEntity.__table__
    
    mapper_registry.map_imperatively(
        Outbox,
        outbox_table,
    )
