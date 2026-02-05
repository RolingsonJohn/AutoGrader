"""
Configuration module using Pydantic Settings for environment management.
Provides centralized, validated configuration across the application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI Configuration
    fastapi_debug: bool = Field(default=False, alias="FASTAPI_DEBUG")
    fastapi_host: str = Field(default="0.0.0.0", alias="FASTAPI_HOST")
    fastapi_port: int = Field(default=8001, alias="FASTAPI_PORT")
    
    # API Configuration
    api_base_url: str = Field(default="http://localhost:8001", alias="API_BASE_URL")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")
    
    # LLM Configuration
    ollama_model: str = Field(default="llama3.1:latest", alias="OLLAMA_MODEL")
    groq_model: str = Field(default="deepseek-r1-distill-llama-70b", alias="GROQ_MODEL")
    genai_model: str = Field(default="gemini-2.0-flash", alias="GENAI_MODEL")
    max_threads: int = Field(default=1, alias="MAX_THREADS")
    api_key_groq: Optional[str] = Field(default=None, alias="API_KEY_GROQ")
    api_key_google: Optional[str] = Field(default=None, alias="API_KEY_GOOGLE")
    exe_method: str = Field(default="ollama", alias="EXE_METHOD")
    
    # RAG Configuration
    tokenizer: str = Field(
        default="sentence-transformers/codebert-base",
        alias="TOKENIZER"
    )
    rag_model: str = Field(default="", alias="RAG_MODEL")
    clf_model: str = Field(default="", alias="CLF_MODEL")
    chroma_path: str = Field(default="./resources", alias="CHROMA_PATH")
    
    # Docker Configuration
    docker_host: str = Field(default="unix:///var/run/docker.sock", alias="DOCKER_HOST")
    docker_image: str = Field(default="sandbox:1", alias="DOCKER_IMAGE")
    
    # Mail Configuration
    mail_authority: str = Field(
        default="https://login.microsoftonline.com/common",
        alias="MAIL_AUTHORITY"
    )
    mail_scopes: str = Field(
        default="https://graph.microsoft.com/Mail.Send",
        alias="MAIL_SCOPES"
    )
    mail_client_id: str = Field(
        default="",
        alias="MICROSOFT_CLIENT_ID"
    )
    mail_endpoint: str = Field(
        default="https://graph.microsoft.com/v1.0/me/sendMail",
        alias="MAIL_ENDPOINT"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"
    
    @field_validator("max_threads", "request_timeout", "max_retries")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Value must be positive")
        return v
    
    @field_validator("exe_method")
    @classmethod
    def validate_exe_method(cls, v: str) -> str:
        allowed = {"ollama", "groq", "genai"}
        if v.lower() not in allowed:
            raise ValueError(f"exe_method must be one of {allowed}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()
    
    @property
    def base_dir(self) -> Path:
        """Get the base directory of the application."""
        return Path(__file__).resolve().parent.parent
    
    @property
    def resources_dir(self) -> Path:
        """Get the resources directory path."""
        return self.base_dir / "services" / "resources"


# Global settings instance
settings = Settings()
