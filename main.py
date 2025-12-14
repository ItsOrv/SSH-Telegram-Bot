"""
Main entry point for SSH Telegram Bot.
Initializes and runs the Telegram bot.
"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from bot import (
    start_command, help_command, add_admin, add_server_handler,
    del_server_handler, servers_list, connect_to_server_handler,
    disconnect_from_server_handler, command_handler, callback_handler,
    add_command, remove_command, show_default_commands, error_handler
)
from config import Config
from init_files import initialize_files

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Main function to start the bot."""
    try:
        # Initialize required files
        initialize_files()
        
        # Validate configuration
        Config.validate()
        
        logger.info("Starting bot...")
        app = Application.builder().token(Config.TOKEN).build()

        # Register command handlers
        app.add_handler(CommandHandler('start', start_command))
        app.add_handler(CommandHandler('help', help_command))
        app.add_handler(CommandHandler('add_admin', add_admin))
        app.add_handler(CommandHandler('add_server', add_server_handler))
        app.add_handler(CommandHandler('del_server', del_server_handler))
        app.add_handler(CommandHandler('servers_list', servers_list))
        app.add_handler(CommandHandler('connect', connect_to_server_handler))
        app.add_handler(CommandHandler('disconnect', disconnect_from_server_handler))
        app.add_handler(CommandHandler('add_command', add_command))
        app.add_handler(CommandHandler('remove_command', remove_command))

        # Register callback query handler for inline buttons
        app.add_handler(CallbackQueryHandler(callback_handler))

        # Register message handler for command execution
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_handler))

        # Register error handler
        app.add_error_handler(error_handler)

        logger.info("Bot is running...")
        app.run_polling(poll_interval=3, drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
