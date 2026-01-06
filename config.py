import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration settings for speed monitor"""
    TEST_INTERVAL_MINUTES: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 10
    DATA_FILE: str = "speed_data.csv"
    LOG_FILE: str = "speed_monitor.log"
    IMMEDIATE_TEST: bool = True
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            TEST_INTERVAL_MINUTES=int(os.getenv('TEST_INTERVAL', '30')),
            MAX_RETRIES=int(os.getenv('MAX_RETRIES', '3')),
            IMMEDIATE_TEST=os.getenv('IMMEDIATE_TEST', 'true').lower() == 'true'
        )

config = Config()