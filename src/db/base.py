import sqlalchemy as sa
from sqlalchemy.orm import registry

metadata = sa.MetaData()
mapper_registry = registry(metadata=metadata)
Base = mapper_registry.generate_base()
