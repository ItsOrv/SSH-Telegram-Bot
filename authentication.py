"""
Authentication module for SSH Telegram Bot.
Handles admin user management and validation.
"""
import os
import logging
from typing import Union
from config import Config

logger = logging.getLogger(__name__)


def is_admin_user(user_id: Union[int, str]) -> bool:
    """
    Check if a user is an admin.
    
    Args:
        user_id: User ID (int) or username (str) to check
        
    Returns:
        True if user is admin, False otherwise
    """
    try:
        if not os.path.exists(Config.ADMINS_FILE):
            logger.warning(f"Admins file not found: {Config.ADMINS_FILE}")
            return False
        
        with open(Config.ADMINS_FILE, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return False
            
            # Split by comma and check if user_id is in the list
            admins = [admin.strip() for admin in content.split(',') if admin.strip()]
            return str(user_id) in admins
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False


def add_admin_to_file(new_admin: str) -> bool:
    """
    Add a new admin to the admins file.
    
    Args:
        new_admin: Admin ID or username to add
        
    Returns:
        True if successful, False otherwise
    """
    try:
        new_admin = str(new_admin).strip()
        if not new_admin:
            logger.warning("Empty admin ID provided")
            return False
        
        # Check if already admin
        if is_admin_user(new_admin):
            logger.info(f"User {new_admin} is already an admin")
            return True
        
        # Create file if it doesn't exist
        file_exists = os.path.exists(Config.ADMINS_FILE)
        
        with open(Config.ADMINS_FILE, 'a', encoding='utf-8') as file:
            if file_exists:
                file.write(f",{new_admin}")
            else:
                file.write(new_admin)
        
        logger.info(f"Admin {new_admin} added successfully")
        return True
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        return False


def remove_admin(admin_id: str) -> bool:
    """
    Remove an admin from the admins file.
    
    Args:
        admin_id: Admin ID to remove
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(Config.ADMINS_FILE):
            return False
        
        with open(Config.ADMINS_FILE, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return False
            
            admins = [admin.strip() for admin in content.split(',') if admin.strip()]
            if str(admin_id) not in admins:
                return False
            
            admins.remove(str(admin_id))
        
        with open(Config.ADMINS_FILE, 'w', encoding='utf-8') as file:
            file.write(','.join(admins))
        
        logger.info(f"Admin {admin_id} removed successfully")
        return True
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        return False
