"""
Server management module for SSH Telegram Bot.
Handles SSH connections, server data management, and command execution.
"""
import csv
import ipaddress
import os
import paramiko
import logging
import threading
import time
from typing import Optional, List, Tuple
from config import Config

logger = logging.getLogger(__name__)

# Global SSH client instance
_ssh_client: Optional[paramiko.SSHClient] = None
_connection_lock = threading.Lock()
_is_connected = False
_connected_server_info: Optional[dict] = None


def get_ssh_client() -> paramiko.SSHClient:
    """
    Get or create SSH client instance.
    
    Returns:
        SSH client instance
    """
    global _ssh_client
    if _ssh_client is None:
        _ssh_client = paramiko.SSHClient()
        _ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return _ssh_client


def is_connected_to_server() -> bool:
    """
    Check if currently connected to a server.
    
    Returns:
        True if connected, False otherwise
    """
    return _is_connected


def get_connected_server_info() -> Optional[dict]:
    """
    Get information about currently connected server.
    
    Returns:
        Server info dict or None
    """
    return _connected_server_info


def is_valid_ip(ip: str) -> bool:
    """
    Validate IP address.
    
    Args:
        ip: IP address string to validate
        
    Returns:
        True if valid IP, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_valid_login(server_ip: str, username: str, password: str, timeout: int = 5) -> bool:
    """
    Validate SSH login credentials by attempting connection.
    
    Args:
        server_ip: Server IP address
        username: SSH username
        password: SSH password
        timeout: Connection timeout in seconds
        
    Returns:
        True if credentials are valid, False otherwise
    """
    test_client = None
    try:
        test_client = paramiko.SSHClient()
        test_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        test_client.connect(
            server_ip,
            username=username,
            password=password,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False
        )
        return True
    except Exception as e:
        logger.warning(f"Login validation failed for {server_ip}: {e}")
        return False
    finally:
        if test_client:
            try:
                test_client.close()
            except Exception:
                pass


def get_servers_data() -> List[List[str]]:
    """
    Read server data from CSV file.
    
    Returns:
        List of server data rows
    """
    servers = []
    try:
        if not os.path.exists(Config.SERVERS_FILE):
            logger.warning(f"Servers file not found: {Config.SERVERS_FILE}")
            return servers
        
        with open(Config.SERVERS_FILE, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for line_count, row in enumerate(csv_reader):
                if line_count > 0 and len(row) >= 3:  # Skip header and validate row
                    servers.append(row)
            logger.info(f"Loaded {len(servers)} servers from file")
    except Exception as e:
        logger.error(f"Error reading servers data: {e}")
    return servers


def add_server(server_ip: str, username: str, password: str, sender: str, timestamp: str) -> bool:
    """
    Add a new server to the servers file.
    
    Args:
        server_ip: Server IP address
        username: SSH username
        password: SSH password
        sender: User ID who added the server
        timestamp: Timestamp when server was added
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_exists = os.path.exists(Config.SERVERS_FILE)
        
        with open(Config.SERVERS_FILE, 'a', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            if not file_exists:
                # Write header if file is new
                csv_writer.writerow(['SERVER_IP', 'LOGIN_USERNAME', 'LOGIN_PASSWORD', 'ADDED_BY', 'DATE_ADDED'])
            csv_writer.writerow([server_ip, username, password, sender, timestamp])
        
        logger.info(f"Server {server_ip} added successfully by {sender}")
        return True
    except Exception as e:
        logger.error(f"Error adding server: {e}")
        return False


def del_server(server_number: int) -> bool:
    """
    Delete a server from the servers file.
    
    Args:
        server_number: 1-based server number to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(Config.SERVERS_FILE):
            return False
        
        servers = get_servers_data()
        if server_number < 1 or server_number > len(servers):
            return False
        
        # Remove the server (server_number is 1-based, so subtract 1)
        removed_server = servers.pop(server_number - 1)
        
        # Write back to file
        with open(Config.SERVERS_FILE, 'w', encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(['SERVER_IP', 'LOGIN_USERNAME', 'LOGIN_PASSWORD', 'ADDED_BY', 'DATE_ADDED'])
            for server in servers:
                csv_writer.writerow(server)
        
        logger.info(f"Server {removed_server[0]} deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting server: {e}")
        return False


def connect_to_server(server_ip: str, username: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Connect to an SSH server.
    
    Args:
        server_ip: Server IP address
        username: SSH username
        password: SSH password
        
    Returns:
        Tuple of (success, error_message)
    """
    global _is_connected, _connected_server_info, _ssh_client
    
    with _connection_lock:
        if _is_connected:
            return False, "Already connected to a server. Please disconnect first."
        
        try:
            client = get_ssh_client()
            client.connect(
                server_ip,
                username=username,
                password=password,
                timeout=Config.SSH_CONNECTION_TIMEOUT,
                allow_agent=False,
                look_for_keys=False
            )
            _is_connected = True
            _connected_server_info = {
                'ip': server_ip,
                'username': username,
                'connected_at': time.time()
            }
            logger.info(f"Successfully connected to {server_ip}")
            return True, None
        except paramiko.AuthenticationException:
            error_msg = "Authentication failed. Check username and password."
            logger.error(f"Connection failed to {server_ip}: {error_msg}")
            return False, error_msg
        except paramiko.SSHException as e:
            error_msg = f"SSH connection error: {str(e)}"
            logger.error(f"Connection failed to {server_ip}: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(f"Connection failed to {server_ip}: {error_msg}")
            return False, error_msg


def disconnect_from_server() -> bool:
    """
    Disconnect from the current SSH server.
    
    Returns:
        True if successful, False otherwise
    """
    global _is_connected, _connected_server_info, _ssh_client
    
    with _connection_lock:
        if not _is_connected:
            return False
        
        try:
            if _ssh_client:
                _ssh_client.close()
                _ssh_client = None
            _is_connected = False
            _connected_server_info = None
            logger.info("Disconnected from server")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
            _is_connected = False
            _connected_server_info = None
            return False


def do_command(command: str, timeout: int = 30) -> Tuple[str, Optional[str]]:
    """
    Execute a command on the connected SSH server.
    
    Args:
        command: Command to execute
        timeout: Command timeout in seconds
        
    Returns:
        Tuple of (stdout, stderr)
    """
    global _ssh_client, _is_connected
    
    if not _is_connected or _ssh_client is None:
        return "", "Not connected to any server"
    
    try:
        stdin, stdout, stderr = _ssh_client.exec_command(command, timeout=timeout)
        stdout_text = ''.join(stdout.readlines())
        stderr_text = ''.join(stderr.readlines())
        return stdout_text, stderr_text if stderr_text else None
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return "", f"Command execution failed: {str(e)}"
