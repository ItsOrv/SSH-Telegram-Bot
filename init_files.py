"""
File initialization module.
Ensures required files exist with proper structure.
"""
import os
import csv
import logging
from config import Config

logger = logging.getLogger(__name__)


def initialize_files():
    """Initialize required files if they don't exist."""
    # Initialize admins.txt
    if not os.path.exists(Config.ADMINS_FILE):
        logger.info(f"Creating {Config.ADMINS_FILE}")
        with open(Config.ADMINS_FILE, 'w', encoding='utf-8') as f:
            # File will be empty initially, admin should be added via /add_admin
            pass
    
    # Initialize servers.txt with header
    if not os.path.exists(Config.SERVERS_FILE):
        logger.info(f"Creating {Config.SERVERS_FILE}")
        with open(Config.SERVERS_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['SERVER_IP', 'LOGIN_USERNAME', 'LOGIN_PASSWORD', 'ADDED_BY', 'DATE_ADDED'])
    
    # Initialize commands.txt
    if not os.path.exists(Config.COMMANDS_FILE):
        logger.info(f"Creating {Config.COMMANDS_FILE}")
        with open(Config.COMMANDS_FILE, 'w', encoding='utf-8') as f:
            # File will be empty initially
            pass
    
    logger.info("File initialization complete")

