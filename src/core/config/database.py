from pydantic import PostgresDsn


class DatabaseSettings:
    def __init__(self, database_uri: PostgresDsn | str):
        self.database_uri = database_uri

    @property
    def asyncpg_uri(self):
        s = str(self.database_uri)

        if "asyncpg" not in s:
            return s.replace("postgresql", "postgresql+asyncpg")

        return s
