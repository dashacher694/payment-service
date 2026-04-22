import os
from dotenv import load_dotenv

load_dotenv()

from src.core.config.database import DatabaseSettings
from src.core.config.rabbitmq import RabbitMQSettings
from src.core.config.server import ServerSettings
from src.core.config.api import APISettings


class ApplicationSettings:
    def __init__(self):
        pg_connection_string = os.getenv("PG_CONNECTION_STRING")
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        api_key = os.getenv("API_KEY")
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))

        if not pg_connection_string:
            raise ValueError("PG_CONNECTION_STRING environment variable is required")

        if not rabbitmq_url:
            raise ValueError("RABBITMQ_URL environment variable is required")

        if not api_key:
            raise ValueError("API_KEY environment variable is required")

        self.db = DatabaseSettings(database_uri=pg_connection_string)
        self.rabbitmq = RabbitMQSettings(rabbitmq_url=rabbitmq_url)
        self.server = ServerSettings(host=host, port=port)
        self.api = APISettings(api_key=api_key)


settings = ApplicationSettings()
