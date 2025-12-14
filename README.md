# SSH Telegram Bot

A secure Telegram bot for managing and executing commands on remote SSH servers through Telegram interface.

## Overview

SSH Telegram Bot provides a convenient way to manage multiple SSH servers and execute commands remotely via Telegram. The bot features role-based access control, command validation, and an intuitive inline keyboard interface.

## Features

- **Multi-Server Management**: Add, remove, and manage multiple SSH servers
- **Remote Command Execution**: Execute commands on connected servers through Telegram
- **Admin Access Control**: Role-based authentication with admin management
- **Command Validation**: Built-in security to prevent dangerous command execution
- **Interactive Interface**: Inline keyboard for easy navigation
- **Default Commands**: Save and manage frequently used commands
- **Connection Management**: Connect and disconnect from servers on demand
- **Input Sanitization**: Protection against command injection attacks

## Requirements

- Python 3.8 or higher
- Telegram Bot Token from [BotFather](https://t.me/botfather)
- Telegram User ID (obtain from [@userinfobot](https://t.me/userinfobot))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ItsOrv/SSH-TelegramBot.git
   cd SSH-TelegramBot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   
   Create a `.env` file in the project root:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   BOT_USERNAME=@your_bot_username
   SSH_TIMEOUT=10
   SSH_CONNECTION_TIMEOUT=5
   ```
   
   Alternatively, set environment variables directly:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   export BOT_USERNAME=@your_bot_username
   ```

4. Initialize admin access:
   
   The bot creates `admins.txt` on first run. Add your Telegram User ID:
   ```bash
   echo "YOUR_TELEGRAM_USER_ID" > admins.txt
   ```
   
   Or use the bot command after starting:
   ```
   /add_admin YOUR_TELEGRAM_USER_ID
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Usage

### Basic Commands

- `/start` - Display main menu with inline keyboard
- `/help` - Show help message with available commands

### Server Management (Admin Only)

- `/add_server [IP] [Username] [Password]` - Add a new SSH server
  ```
  Example: /add_server 192.168.1.1 root mypassword
  ```

- `/servers_list` - List all configured servers

- `/del_server [Number]` - Delete a server by number
  ```
  Example: /del_server 1
  ```

### Connection Management (Admin Only)

- `/connect [Number]` - Connect to a server by number
  ```
  Example: /connect 1
  ```

- `/disconnect` - Disconnect from the current server

### Command Execution

After connecting to a server, send any command as a text message. The bot executes it on the connected server and returns the output.

**Note**: The bot validates commands to prevent dangerous operations. Some commands may be blocked for security reasons.

### Default Commands Management

- `/add_command [Command]` - Add a command to the default commands list
- `/remove_command [Number]` - Remove a command from the list

### Admin Management (Admin Only)

- `/add_admin [ID]` - Add a new admin user

## Project Structure

```
SSH-Telegram-Bot/
├── main.py              # Application entry point
├── bot.py               # Bot command handlers and message processing
├── config.py            # Configuration management
├── authentication.py    # Admin authentication and authorization
├── servers.py           # SSH server management and connections
├── utils.py             # Utility functions and validators
├── init_files.py        # File initialization
├── requirements.txt     # Python dependencies
├── admins.txt           # Admin user IDs (auto-created)
├── servers.txt          # Server list in CSV format (auto-created)
└── commands.txt         # Default commands list (auto-created)
```

## Configuration

### Environment Variables

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (required)
- `BOT_USERNAME` - Your bot username (optional)
- `SSH_TIMEOUT` - Command execution timeout in seconds (default: 10)
- `SSH_CONNECTION_TIMEOUT` - Connection timeout in seconds (default: 5)

### Security Settings

Security settings can be customized in `config.py`:

- `ALLOWED_COMMAND_PREFIXES` - List of allowed command prefixes
- `BLOCKED_COMMANDS` - List of blocked command patterns

## Security Considerations

**Important Security Notes:**

1. **Password Storage**: Passwords are stored in plain text in `servers.txt`. For production use, implement encryption.

2. **Command Validation**: The bot includes basic command validation. Review and customize:
   - `BLOCKED_COMMANDS` in `config.py`
   - `ALLOWED_COMMAND_PREFIXES` if needed
   - Monitor command execution logs

3. **Admin Access**: Keep `admins.txt` secure and only grant admin access to trusted users.

4. **Network Security**: Ensure SSH servers are properly secured:
   - Strong passwords or SSH key authentication
   - Firewall rules
   - Regular security updates
   - Disable root login if possible

5. **File Permissions**: Restrict file permissions on sensitive files:
   ```bash
   chmod 600 admins.txt servers.txt
   ```

## Troubleshooting

### Bot does not start

- Verify `TELEGRAM_BOT_TOKEN` is set correctly
- Check token validity with BotFather
- Ensure all dependencies are installed

### Cannot connect to servers

- Verify server IP, username, and password are correct
- Check network connectivity
- Ensure SSH service is running on target server
- Review firewall rules
- Check SSH connection timeout settings

### Permission denied errors

- Verify your user ID is in `admins.txt`
- Use `/add_admin` command to add yourself
- Check file permissions

### Command execution fails

- Verify connection to server is active
- Check command syntax
- Review blocked commands list
- Check command timeout settings

## Dependencies

- `paramiko==3.4.0` - SSH client library
- `python-telegram-bot==20.7` - Telegram Bot API
- `python-dotenv==1.0.0` - Environment variable management
- `requests==2.31.0` - HTTP library

## Contributing

Contributions are welcome. Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is open source. Please check the repository for license information.

## Repository

[GitHub Repository](https://github.com/ItsOrv/SSH-TelegramBot)
