"""
Configuration settings for VITA-BAND AI Backend
"""
import os

class Settings:
    PROJECT_NAME: str = "VITA-BAND AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Mode: DEMO or HARDWARE
    OPERATION_MODE: str = os.getenv("OPERATION_MODE", "DEMO")
    
    # Simulation settings
    DEFAULT_SIMULATION_INTERVAL_SEC: float = 0.5  # 2 Hz telemetry updates
    SIMULATION_NOISE_LEVEL: float = 0.05
    
    # Emergency Alert settings
    EMERGENCY_COUNTDOWN_SEC: int = 15
    PRIMARY_EMERGENCY_CONTACT: str = os.getenv("PRIMARY_EMERGENCY_CONTACT", "+91 9876543210")
    
    # Local Storage
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "vita_band.db")

    # CORS Configuration
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def cors_origins_list(self) -> list:
        if not self.CORS_ORIGINS or self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
