import time
import requests
import sys
from datetime import datetime, timezone

class ActiveNodeNotFoundError(Exception):
    """Custom exception raised when no active Vault node is found."""
    pass

def get_active_node(servers, retries=3, interval=5):
    """
    Check a list of Vault servers' HA status and return the active node(leader).

    Parameters:
        servers (list): List of Vault server URLs.
        retries (int): Number of retries for each server. Default is 3.
        interval (int): Time in seconds between retries. Default is 5 seconds.

    Returns:
        str: The API address of the active Vault node.

    Raises:
        ActiveNodeNotFoundError: If no active node is found after all retries.
    """
    for server in servers:
        for attempt in range(retries):
            try:
                # Make a request to the Vault HA status endpoint
                response = requests.get(f"{server}/v1/sys/ha-status")
                response.raise_for_status()
                data = response.json()

                # Check the Nodes list for the active node
                for node in data.get("Nodes", []):
                    if node.get("active_node"):
                        return node.get("api_address")

            except requests.exceptions.RequestException as e:
                print(f"Error connecting to {server}: {e}")

            # Wait for the specified interval before retrying
            if attempt < retries - 1:
                time.sleep(interval)

    # If no active node is found, raise an exception
    raise ActiveNodeNotFoundError("No active Vault node found after checking all servers and retries.")

def check_token_expiry(vault_addr, vault_token, days_left):
    """
    Checks the Vault token's expiration date via the /v1/auth/token/lookup-self API.

    If the token is going to expire in 'days_left' or less, the script exits with a message.

    Args:
    vault_addr (str): The Vault address.
    vault_token (str): The Vault authentication token.
    days_left (int): Number of days before the token expiry to trigger the warning.
    """
    lookup_url = f"{vault_addr}/v1/auth/token/lookup-self"
    headers = {"X-Vault-Token": vault_token}

    try:
        response = requests.get(lookup_url, headers=headers)
        response.raise_for_status()

        token_data = response.json()["data"]
        expire_time_str = token_data.get("expire_time")

        if expire_time_str:
            expire_time = datetime.fromisoformat(expire_time_str.rstrip("Z"))  # Handle Zulu time zone format
            current_time = datetime.now(timezone.utc)
            days_left_to_expire = (expire_time - current_time).days

            if days_left_to_expire <= days_left:
                print(f"Token will expire in {days_left_to_expire} days. Exiting...")
                sys.exit(1)
        else:
            print("Token does not have an expiration time.")
    except requests.RequestException as e:
        print(f"Error checking token expiration: {e}")
        sys.exit(1)

