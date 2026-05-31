from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str = "divyanshyadav"
    db_password: str 
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "customer_db"

    @property
    def database_url(self):
        return (
            f"postgresql+psycopg://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}"
            f"/{self.db_name}"
        )

    model_config = SettingsConfigDict(

        env_file=".env"

    )


settings = Settings()

if __name__=="__main__":
    print(settings.database_url)