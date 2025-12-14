"""
Utility functions for SSH Telegram Bot.
Contains helper functions for validation, logging, and common operations.
"""
import logging
import re
from typing import Optional, Tuple, List
from telegram import Update

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_user_info(update: Update) -> Tuple[Optional[int], Optional[str]]:
    """
    Extract user information from update object.
    
    Args:
        update: Telegram update object
        
    Returns:
        Tuple of (chat_id, username)
    """
    if update.message:
        return update.message.chat.id, update.message.chat.username
    elif update.callback_query:
        return update.callback_query.message.chat.id, update.callback_query.from_user.username
    return None, None


def validate_command(command: str, blocked_commands: List[str], allowed_prefixes: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate SSH command for security.
    
    Args:
        command: Command string to validate
        blocked_commands: List of blocked command patterns
        allowed_prefixes: Optional list of allowed command prefixes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    command = command.strip()
    
    # Check for blocked commands
    for blocked in blocked_commands:
        if blocked.lower() in command.lower():
            return False, f"Command contains blocked pattern: {blocked}"
    
    # Check for dangerous patterns
    dangerous_patterns = [
        r';\s*rm\s+-rf',
        r'&&\s*rm\s+-rf',
        r'\|\s*rm\s+-rf',
        r'>\s*/dev/',
        r'<\s*/dev/',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, "Command contains dangerous pattern"
    
    # If allowed_prefixes is specified, check if command starts with one
    if allowed_prefixes:
        command_parts = command.split()
        if command_parts:
            first_word = command_parts[0].lower()
            if not any(first_word.startswith(prefix) for prefix in allowed_prefixes):
                return False, f"Command must start with one of: {', '.join(allowed_prefixes)}"
    
    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # Limit length
    if len(text) > 1000:
        text = text[:1000]
    return text.strip()


def format_server_list(servers: List[List[str]]) -> str:
    """
    Format server list for display.
    
    Args:
        servers: List of server data
        
    Returns:
        Formatted string
    """
    if not servers:
        return "No servers found."
    
    table = "All Servers:\n\n"
    for idx, server in enumerate(servers, start=1):
        table += (
            f"Server Number: {idx}\n"
            f"Server IP: {server[0]}\n"
            f"Added By: {server[3]}\n"
            f"Date Added: {server[4]}\n"
            f"{'-' * 20}\n\n"
        )
    return table

