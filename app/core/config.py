# verify_project/app/core/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# It's good practice to load .env file as early as possible
# and preferably only once in the application lifecycle.
# The path to .env can be made more robust if needed, e.g., by constructing from __file__
# For simplicity, assuming .env is in the project root where the app is run.
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=dotenv_path)

class Settings(BaseSettings):
    """
    Application settings.
    Values are loaded from environment variables.
    The .env file is loaded by load_dotenv() above.
    """
    VERIFY_API_KEY: str
    SMS_API_KEY: str
    SMS_API_URL: str
    SMS_SENDER_NUMBER: str
    OTP_EXPIRY_SECONDS: int  # Default 5 minutes
    OPENAI_API_URL: str
    OPENAI_API_KEY: str

    # Pydantic-settings configuration
    # For Pydantic V2, model_config is used instead of class Config
    model_config = SettingsConfigDict(
        env_file=dotenv_path,  # Specify .env file (though load_dotenv already handles it)
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields from .env if any
    )

# Create a single instance of the settings to be imported by other modules
settings = Settings(
    VERIFY_API_KEY=os.getenv("VERIFY_API_KEY"),
    SMS_API_KEY=os.getenv("SMS_API_KEY"),
    SMS_API_URL=os.getenv("SMS_API_URL"),
    SMS_SENDER_NUMBER=os.getenv("SMS_SENDER_NUMBER"),
    OTP_EXPIRY_SECONDS=int(os.getenv("OTP_EXPIRY_SECONDS")),
    OPENAI_API_URL=os.getenv("OPENAI_API_URL"),
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
)
