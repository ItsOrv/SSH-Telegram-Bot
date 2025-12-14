"""
Configuration management module for SSH Telegram Bot.
Handles environment variables and configuration settings.
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for bot settings."""
    
    # Telegram Bot Configuration
    TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    BOT_USERNAME: str = os.getenv('BOT_USERNAME', '')
    
    # File paths
    ADMINS_FILE: str = 'admins.txt'
    SERVERS_FILE: str = 'servers.txt'
    COMMANDS_FILE: str = 'commands.txt'
    
    # SSH Connection Settings
    SSH_TIMEOUT: int = int(os.getenv('SSH_TIMEOUT', '10'))
    SSH_CONNECTION_TIMEOUT: int = int(os.getenv('SSH_CONNECTION_TIMEOUT', '5'))
    
    # Security Settings
    ALLOWED_COMMAND_PREFIXES: List[str] = ['ls', 'cd', 'pwd', 'cat', 'grep', 'find', 'ps', 'top', 'df', 'du', 'free', 'uptime']
    BLOCKED_COMMANDS: List[str] = ['rm -rf /', 'mkfs', 'dd if=', 'format', 'fdisk']
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required. Set it in .env file or environment variable.")
        return True

