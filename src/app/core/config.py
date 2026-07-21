import os


class Settings:
    def __init__(self) -> None:
        self.app_env = os.getenv("APP_ENV", "development")
        self.app_port = int(os.getenv("APP_PORT", "8000"))
        self.database_url = os.getenv(
            "DATABASE_URL",
            os.getenv("LOCAL_DATABASE_URL", "postgresql://user:password@localhost:5432/product_catalog"),
        )


settings = Settings()
