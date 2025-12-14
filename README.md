# SSH Telegram Bot

This bot helps you to manage and interact with your servers CLI through SSH protocol using Telegram.

## Features

- **Secure SSH Management**: Connect to multiple SSH servers through Telegram
- **Command Execution**: Execute commands on connected servers
- **Server Management**: Add, remove, and list SSH servers
- **Admin Control**: Role-based access control with admin management
- **Command Validation**: Built-in security to prevent dangerous commands
- **User-Friendly Interface**: Inline keyboard for easy navigation

## Security Features

- Command injection protection
- Input validation and sanitization
- Dangerous command blocking
- Secure credential storage (note: passwords are stored in plain text - consider encryption for production)
- Admin-only access for sensitive operations

## Setup Guide

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Your Telegram User ID (get it from [@userinfobot](https://t.me/userinfobot))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ItsOrv/SSH-TelegramBot.git
   cd SSH-TelegramBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   BOT_USERNAME=@your_bot_username
   ```
   
   Alternatively, you can set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   export BOT_USERNAME=@your_bot_username
   ```

4. **Set up admin access**
   
   The bot will create `admins.txt` on first run. Add your Telegram User ID:
   ```bash
   echo "YOUR_TELEGRAM_USER_ID" > admins.txt
   ```
   
   Or use the bot command after starting:
   ```
   /add_admin YOUR_TELEGRAM_USER_ID
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## Commands and Usage

### Basic Commands

- `/start` - Show main menu with inline keyboard
- `/help` - Show help message with all available commands

### Server Management (Admin Only)

- `/add_server [IP] [Username] [Password]` - Add a new SSH server
  ```
  Example: /add_server 192.168.1.1 root mypassword
  ```
  
- `/servers_list` - List all added servers
  
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

After connecting to a server, you can send any command as a text message. The bot will execute it on the connected server and return the output.

**Note**: The bot validates commands to prevent dangerous operations. Some commands may be blocked for security reasons.

### Default Commands Management

- `/add_command [Command]` - Add a command to the default commands list
- `/remove_command [Number]` - Remove a command from the list

### Admin Management (Admin Only)

- `/add_admin [ID]` - Add a new admin user

## Project Structure

```
SSH-Telegram-Bot/
├── main.py              # Main entry point
├── bot.py               # Bot command handlers
├── config.py            # Configuration management
├── authentication.py    # Admin authentication
├── servers.py           # SSH server management
├── utils.py             # Utility functions
├── init_files.py        # File initialization
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── admins.txt           # Admin user IDs (auto-created)
├── servers.txt          # Server list (auto-created)
└── commands.txt         # Default commands (auto-created)
```

## Configuration

You can customize the bot behavior by setting environment variables:

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (required)
- `BOT_USERNAME` - Your bot username (optional)
- `SSH_TIMEOUT` - Command execution timeout in seconds (default: 10)
- `SSH_CONNECTION_TIMEOUT` - Connection timeout in seconds (default: 5)

## Security Considerations

⚠️ **Important Security Notes:**

1. **Password Storage**: Passwords are currently stored in plain text in `servers.txt`. For production use, consider implementing encryption.

2. **Command Validation**: The bot includes basic command validation, but you should:
   - Review and customize `BLOCKED_COMMANDS` in `config.py`
   - Adjust `ALLOWED_COMMAND_PREFIXES` if needed
   - Monitor command execution logs

3. **Admin Access**: Keep `admins.txt` secure and only grant admin access to trusted users.

4. **Network Security**: Ensure your SSH servers are properly secured with:
   - Strong passwords or SSH keys
   - Firewall rules
   - Regular security updates

## Troubleshooting

### Bot doesn't start
- Check that `TELEGRAM_BOT_TOKEN` is set correctly
- Verify the token is valid by testing with BotFather

### Can't connect to servers
- Verify server IP, username, and password are correct
- Check network connectivity
- Ensure SSH service is running on the target server
- Check firewall rules

### Permission denied errors
- Make sure your user ID is in `admins.txt`
- Use `/add_admin` command to add yourself

## Contributing

Contributions of all sizes are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source. Please check the repository for license information.

## Todo

- [ ] Add option to download files
- [ ] Add option to upload files
- [ ] Add interactive commands
- [ ] Optimize output formatting
- [ ] Add encryption for stored passwords
- [ ] Add SSH key authentication support
- [ ] Add connection pooling
- [ ] Add command history

## Support

For issues and questions, please check the [GitHub repository](https://github.com/ItsOrv/SSH-TelegramBot).
