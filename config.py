
"""
Configuration file for Blood Transfer Blockchain System
Save as 'config.py'
"""

import os
from typing import Dict, Any

class Config:
    """Configuration settings for the blockchain system"""

    # Blockchain settings
    MINING_DIFFICULTY = 4
    MAX_TRANSACTIONS_PER_BLOCK = 10
    MINING_REWARD = 100
    GENESIS_HOSPITAL = "SYSTEM"

    # Network settings
    GRPC_PORT = 50051
    GRPC_HOST = "localhost"
    USE_TLS = False

    # Certificate paths (for production TLS)
    TLS_PRIVATE_KEY_PATH = os.getenv("TLS_PRIVATE_KEY_PATH", "certs/server-key.pem")
    TLS_CERTIFICATE_PATH = os.getenv("TLS_CERTIFICATE_PATH", "certs/server-cert.pem")

    # Blood transfer constraints
    MAX_TRANSFER_DISTANCE_KM = 100.0
    MIN_BLOOD_CREDITS_FOR_TRANSFER = 10
    BLOOD_CREDIT_COST_PER_TRANSFER = 5
    BLOOD_CREDIT_REWARD_PER_RECEPTION = 2

    # Tampering and security
    INITIAL_TAMPERING_CREDITS = 2
    REPUTATION_PENALTY_PER_VIOLATION = 15
    MIN_REPUTATION_SCORE = 0
    MAX_REPUTATION_SCORE = 100

    # GPS and location settings
    GPS_ACCURACY_THRESHOLD = 0.001  # degrees
    LOCATION_UPDATE_INTERVAL = 300  # seconds

    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///blood_transfer.db")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "blood_transfer.log")

    # Blood type compatibility matrix
    BLOOD_COMPATIBILITY = {
        "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
        "O+": ["O+", "A+", "B+", "AB+"],
        "A-": ["A-", "A+", "AB-", "AB+"],
        "A+": ["A+", "AB+"],
        "B-": ["B-", "B+", "AB-", "AB+"],
        "B+": ["B+", "AB+"],
        "AB-": ["AB-", "AB+"],
        "AB+": ["AB+"]
    }

    # Blood expiry periods (in days)
    BLOOD_EXPIRY_PERIODS = {
        "whole_blood": 42,
        "red_cells": 42,
        "platelets": 5,
        "plasma": 365,
        "cryoprecipitate": 365
    }

    @classmethod
    def get_compatible_recipients(cls, donor_blood_type: str) -> list:
        """Get list of compatible blood types for a donor"""
        return cls.BLOOD_COMPATIBILITY.get(donor_blood_type, [])

    @classmethod
    def is_compatible(cls, donor_type: str, recipient_type: str) -> bool:
        """Check if donor blood type is compatible with recipient"""
        compatible_types = cls.BLOOD_COMPATIBILITY.get(donor_type, [])
        return recipient_type in compatible_types

    @classmethod
    def load_from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            'mining_difficulty': int(os.getenv('MINING_DIFFICULTY', cls.MINING_DIFFICULTY)),
            'grpc_port': int(os.getenv('GRPC_PORT', cls.GRPC_PORT)),
            'grpc_host': os.getenv('GRPC_HOST', cls.GRPC_HOST),
            'use_tls': os.getenv('USE_TLS', str(cls.USE_TLS)).lower() == 'true',
            'max_transfer_distance': float(os.getenv('MAX_TRANSFER_DISTANCE_KM', cls.MAX_TRANSFER_DISTANCE_KM)),
            'log_level': os.getenv('LOG_LEVEL', cls.LOG_LEVEL),
        }

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    USE_TLS = False
    LOG_LEVEL = "DEBUG"
    MINING_DIFFICULTY = 2  # Easier mining for development

class ProductionConfig(Config):
    """Production environment configuration"""
    USE_TLS = True
    LOG_LEVEL = "WARNING"
    MINING_DIFFICULTY = 6  # Harder mining for production

class TestConfig(Config):
    """Test environment configuration"""
    DATABASE_URL = "sqlite:///test_blood_transfer.db"
    USE_TLS = False
    LOG_LEVEL = "DEBUG"
    MINING_DIFFICULTY = 1  # Minimal mining for tests

# Configuration factory
def get_config(env: str = None) -> Config:
    """Get configuration based on environment"""
    env = env or os.getenv('FLASK_ENV', 'development')

    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestConfig()
    else:
        return DevelopmentConfig()
