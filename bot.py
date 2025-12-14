"""
Main bot module for SSH Telegram Bot.
Handles all Telegram bot commands and interactions.
"""
import os
from time import gmtime, strftime
from typing import Optional, List
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import logging

from authentication import is_admin_user, add_admin_to_file
from servers import (
    get_servers_data, is_valid_ip, is_valid_login, add_server, del_server,
    connect_to_server, disconnect_from_server, do_command, is_connected_to_server,
    get_connected_server_info
)
from utils import get_user_info, validate_command, sanitize_input, format_server_list
from config import Config

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with inline keyboard."""
    keyboard = [
        [InlineKeyboardButton("Add Server", callback_data="add_server")],
        [InlineKeyboardButton("Delete Server", callback_data="del_server")],
        [InlineKeyboardButton("List Servers", callback_data="list_servers")],
        [InlineKeyboardButton("Connect to Server", callback_data="connect_server")],
        [InlineKeyboardButton("Disconnect from Server", callback_data="disconnect_server")],
        [InlineKeyboardButton("Default Commands", callback_data="default_commands")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'Welcome to **SSH Terminal Bot**\nChoose an action:',
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "add_server":
        await query.message.reply_text(
            "To add a server, use the command: /add_server [IP] [Username] [Password]"
        )
    elif query.data == "del_server":
        await query.message.reply_text(
            "To delete a server, use the command: /del_server [Server Number]"
        )
    elif query.data == "list_servers":
        await servers_list(update, context)
    elif query.data == "connect_server":
        await query.message.reply_text(
            "To connect to a server, use the command: /connect [Server Number]"
        )
    elif query.data == "disconnect_server":
        await disconnect_from_server_handler(update, context)
    elif query.data == "default_commands":
        await show_default_commands(update, context)
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "add_command":
        await query.message.reply_text(
            "To add a command, use the command: /add_command [Your Command]"
        )
    elif query.data == "remove_command":
        await query.message.reply_text(
            "To remove a command, use the command: /remove_command [Command Number]"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "Please check the repository for command guides:\n"
        "https://github.com/ItsOrv/SSH-TelegramBot\n\n"
        "Available commands:\n"
        "/start - Show main menu\n"
        "/help - Show this help message\n"
        "/add_admin [ID] - Add an admin (admin only)\n"
        "/add_server [IP] [Username] [Password] - Add a server (admin only)\n"
        "/del_server [Number] - Delete a server (admin only)\n"
        "/servers_list - List all servers (admin only)\n"
        "/connect [Number] - Connect to a server (admin only)\n"
        "/disconnect - Disconnect from server (admin only)\n"
        "/add_command [Command] - Add a default command\n"
        "/remove_command [Number] - Remove a default command"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_admin command."""
    user_chat_id, username = get_user_info(update)
    
    if not is_admin_user(user_chat_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You don't have access to add a new admin."
        )
        return
    
    if not update.message:
        return
    
    data = update.message.text
    processed_data = data.replace("/add_admin", '').strip()
    
    if not processed_data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please provide an admin ID: /add_admin [ID]"
        )
        return
    
    if add_admin_to_file(processed_data):
        logger.info(f"New admin added by ({username} {user_chat_id}): {processed_data}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"New admin added: {processed_data} is now admin."
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to add admin. Please try again."
        )


async def del_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /del_server command."""
    user_chat_id, username = get_user_info(update)

    if not (is_admin_user(user_chat_id) or is_admin_user(username)):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You need admin access to delete a server!"
        )
        return
    
    if not update.message:
        return
    
    try:
        data = update.message.text
        processed_data = data.replace("/del_server", '').strip()
        
        if not processed_data or not processed_data.isdigit():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please provide a valid server number: /del_server [Number]"
            )
            return
        
        server_number = int(processed_data)
        servers = get_servers_data()
        
        if server_number < 1 or server_number > len(servers):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Server doesn't exist. Please try again."
            )
            return
        
        server_info = servers[server_number - 1]
        if del_server(server_number):
            logger.info(
                f"Server deleted by ({username} {user_chat_id}): "
                f"IP={server_info[0]}, User={server_info[1]}"
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f'Server Deleted\n'
                    f'Server IP: {server_info[0]}\n'
                    f'Connection Info: {server_info[1]}:{server_info[2]}\n'
                    f'Deleted by: {user_chat_id} at {strftime("%Y-%m-%d %H:%M:%S", gmtime())}'
                )
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Failed to delete server. Please try again."
            )
    except Exception as e:
        logger.error(f"Error in del_server_handler: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred while deleting the server."
        )


async def add_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_server command."""
    user_chat_id, username = get_user_info(update)
    
    if not (is_admin_user(user_chat_id) or is_admin_user(username)):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You need admin access to add a new server!"
        )
        return
    
    if not update.message:
        return
    
    try:
        data = update.message.text
        processed_data = data.replace("/add_server", '').strip()
        processed_data_list = processed_data.split()
        
        if len(processed_data_list) < 3:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please provide IP, username, and password: /add_server [IP] [Username] [Password]"
            )
            return
        
        server_ip = processed_data_list[0]
        server_username = processed_data_list[1]
        server_password = processed_data_list[2]
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Checking validity of given IP..."
        )
        
        if not is_valid_ip(server_ip):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Adding new server failed! Please enter a valid IP."
            )
            return
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="IP validation successful. Checking login information..."
        )
        
        if not is_valid_login(server_ip, server_username, server_password):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Adding new server failed! Either username or password is incorrect. Please try again."
            )
            return
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Login information validation successful. Adding server..."
        )
        
        timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if add_server(server_ip, server_username, server_password, str(user_chat_id), timestamp):
            logger.info(
                f"New server added by ({username} {user_chat_id}): {server_ip}"
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    f'New server added!\n'
                    f'Server IP: {server_ip}\n'
                    f'Connection Info: {server_username}:{server_password}\n'
                    f'Added by: {user_chat_id} at {timestamp}'
                )
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Failed to add server. Please try again."
            )
    except Exception as e:
        logger.error(f"Error in add_server_handler: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred while adding the server."
        )


async def servers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /servers_list command."""
    user_chat_id, username = get_user_info(update)
    
    if not (is_admin_user(user_chat_id) or is_admin_user(username)):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You need admin access to view list of servers!"
        )
        return
    
    logger.info(f"List of servers asked by: ({username} {user_chat_id})")
    servers = get_servers_data()
    table = format_server_list(servers)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=table)


async def connect_to_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /connect command."""
    user_chat_id, username = get_user_info(update)
    
    if not (is_admin_user(user_chat_id) or is_admin_user(username)):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You need admin access to connect to a server!"
        )
        return
    
    if is_connected_to_server():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Already connected to server. Please disconnect first using: /disconnect"
        )
        return
    
    if not update.message:
        return
    
    try:
        data = update.message.text
        processed_data = data.replace("/connect", '').strip()
        
        if not processed_data or not processed_data.isdigit():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please provide a valid server number: /connect [Number]"
            )
            return
        
        server_index = int(processed_data) - 1
        servers = get_servers_data()
        
        if server_index < 0 or server_index >= len(servers):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Invalid server number. Please try again."
            )
            return
        
        server_info = servers[server_index]
        server_ip = server_info[0]
        server_username = server_info[1]
        server_password = server_info[2]
        
        logger.info(
            f"Trying to connect to server by ({username} {user_chat_id}): "
            f"IP={server_ip}, User={server_username}"
        )
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f'Trying to connect to server...\n'
                f'Server IP: {server_ip}\n'
                f'Connection Info: {server_username}:{server_password}\n'
                f'Added by: {server_info[3]} at {server_info[4]}'
            )
        )
        
        success, error_msg = connect_to_server(server_ip, server_username, server_password)
        
        if success:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Successfully connected to server!"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Couldn't connect to server! {error_msg or 'Unknown error'}"
            )
    except Exception as e:
        logger.error(f"Error in connect_to_server_handler: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred while connecting to the server."
        )


async def disconnect_from_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /disconnect command."""
    user_chat_id, username = get_user_info(update)

    if not (is_admin_user(user_chat_id) or is_admin_user(username)):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You need admin access to disconnect from a server!"
        )
        return
    
    logger.info(f"Trying to close connection by ({username} {user_chat_id})")
    
    if disconnect_from_server():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Connection closed!"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to disconnect! (Are you sure you were connected to a server?)"
        )


def get_default_commands() -> List[str]:
    """Get list of default commands from file."""
    commands = []
    try:
        if os.path.exists(Config.COMMANDS_FILE):
            with open(Config.COMMANDS_FILE, 'r', encoding='utf-8') as file:
                commands = [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        logger.error(f"Error reading commands file: {e}")
    return commands


async def show_default_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show default commands with inline keyboard."""
    commands = get_default_commands()
    
    if commands:
        message = "Default Commands:\n\n"
        for idx, command in enumerate(commands, start=1):
            message += f"{idx}. {command}\n"
    else:
        message = "No commands found."

    keyboard = [
        [InlineKeyboardButton("Add Command", callback_data="add_command")],
        [InlineKeyboardButton("Remove Command", callback_data="remove_command")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_command command."""
    if not update.message:
        return
    
    command_text = update.message.text.replace("/add_command", "").strip()
    
    if not command_text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please provide a command to add: /add_command [Your Command]"
        )
        return
    
    try:
        # Validate command
        is_valid, error_msg = validate_command(command_text, Config.BLOCKED_COMMANDS)
        if not is_valid:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Cannot add command: {error_msg}"
            )
            return
        
        # Sanitize command
        command_text = sanitize_input(command_text)
        
        with open(Config.COMMANDS_FILE, 'a', encoding='utf-8') as file:
            file.write(f"{command_text}\n")
        
        logger.info(f"Command added: {command_text}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Command added: `{command_text}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error adding command: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to add command. Please try again."
        )


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remove_command command."""
    if not update.message:
        return
    
    try:
        command_text = update.message.text.replace("/remove_command", "").strip()
        
        if not command_text or not command_text.isdigit():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please provide a valid command number: /remove_command [Number]"
            )
            return
        
        command_index = int(command_text) - 1
        commands = get_default_commands()
        
        if command_index < 0 or command_index >= len(commands):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Invalid command number."
            )
            return
        
        removed_command = commands.pop(command_index)
        
        with open(Config.COMMANDS_FILE, 'w', encoding='utf-8') as file:
            for command in commands:
                file.write(f"{command}\n")
        
        logger.info(f"Command removed: {removed_command}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Command removed: `{removed_command}`",
            parse_mode="Markdown"
        )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please provide a valid command number."
        )
    except Exception as e:
        logger.error(f"Error removing command: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Failed to remove command. Please try again."
        )


def handle_command(text: str) -> str:
    """
    Handle command execution on connected server.
    
    Args:
        text: Command text to execute
        
    Returns:
        Formatted response string
    """
    if not is_connected_to_server():
        return "I'm not connected to any server.\nPlease connect me with /connect command"
    
    # Sanitize and validate command
    sanitized_text = sanitize_input(text)
    is_valid, error_msg = validate_command(sanitized_text, Config.BLOCKED_COMMANDS)
    
    if not is_valid:
        return f"Command rejected: {error_msg}"
    
    try:
        stdout, stderr = do_command(sanitized_text, timeout=Config.SSH_TIMEOUT)
        
        response = f"*Done!*\n```shell\n{sanitized_text}\n```\n\n*Output:*\n```\n{stdout}\n```"
        
        if stderr:
            response += f"\n\n*Errors:*\n```\n{stderr}\n```"
        
        return response
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return f"Command execution failed: {str(e)}"


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages as commands."""
    if not update.message:
        return
    
    message_type = update.message.chat.type
    text = update.message.text
    
    if not text:
        return
    
    logger.info(
        f'User ({update.message.chat.first_name} {update.message.chat.last_name}) '
        f'in {message_type}: "{text}"'
    )
    
    if message_type in ('group', 'supergroup'):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Currently I'm not able to execute commands given in groups!"
        )
        return
    
    response = handle_command(text)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode="Markdown"
    )


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An error occurred. Please try again later."
            )
        except Exception:
            pass
