import time
import requests
import sys
from datetime import datetime, timezone


import time
import requests


class ActiveNodeNotFoundError(Exception):
    """Custom exception raised when no active Vault node is found."""

    pass


def get_leader(servers, retries=3, interval=5):
    """
    Check a list of Vault servers' /sys/leader status and return the leader node.

    Parameters:
        servers (list): List of Vault server URLs.
        retries (int): Number of retries for each server. Default is 3.
        interval (int): Time in seconds between retries. Default is 5 seconds.

    Returns:
        str: The leader address of the active Vault node.

    Raises:
        ActiveNodeNotFoundError: If no active node is found after all retries.
    """
    for server in servers:
        for attempt in range(retries):
            try:
                # Make a request to the Vault leader status endpoint
                response = requests.get(f"{server}/v1/sys/leader")

                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()

                # Check if the server is the leader or if the leader address exists
                if data.get("leader_address"):
                    return data["leader_address"]

            except requests.exceptions.RequestException as e:
                print(f"Error connecting to {server}: {e}")

            # Wait for the specified interval before retrying
            if attempt < retries - 1:
                time.sleep(interval)

    # If no active node is found, raise an exception
    raise ActiveNodeNotFoundError(
        "No Vault leader found after checking all servers and retries."
    )


import requests
from datetime import datetime, timezone

def check_token_expiry(vault_addr, vault_token, days_left):
    """
    Checks the Vault token's expiration date via the /v1/auth/token/lookup-self API.

    If the token is going to expire in 'days_left' or less, returns True and actual days left.
    Otherwise, returns False and actual days left.

    If there is no expiration time, return -1 for actual_days_left

    If encountering any errors, return True and None for actual_days_left, indicating an error.

    Args:
    vault_addr (str): The Vault address.
    vault_token (str): The Vault authentication token.
    days_left (int): Number of days before the token expiry to trigger the warning.

    Returns:
    tuple: (will_expire (bool), actual_days_left (int))
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

            return days_left_to_expire <= days_left, days_left_to_expire
        else:           
            return False, -1
    except requests.RequestException as e:
        print(f"Error checking token expiration: {e}")
        return True, None


def create_batch_token(vault_addr, access_token, ttl, policies=["default"]):
    """
    Create a new Vault batch token using the given access_token.

    Parameters:
    - vault_addr (str): The Vault server address.
    - access_token (str): The token used to authenticate with Vault.
    - ttl (int): Time-to-live for the new token in seconds.
    - policies (list): List of policies for the new token.

    Returns:
    - str: The newly created Vault batch token.
    """

    # Construct the URL
    url = f"{vault_addr}/v1/auth/token/create-orphan"

    # Set the headers
    headers = {"X-Vault-Token": access_token, "Content-Type": "application/json"}

    # Build the request body with token_type set to 'batch'
    payload = {"policies": policies, "ttl": ttl, "type": "batch"}

    try:
        # Make the POST request to Vault
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the response JSON to extract the new token
        data = response.json()
        new_token = data["auth"]["client_token"]
        return new_token

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except Exception as err:
        print(f"An error occurred: {err}")  # Handle other exceptions

    return None  # Return None if token creation fails

def is_sealed(vault_addr):
    """
    Check if the Vault server is sealed.

    Args:
        vault_addr (str): The Vault server address (e.g., "https://vault.example.com").

    Returns:
        bool: True if the Vault is sealed, False otherwise.
    """
    try:
        # Make a GET request to the health endpoint
        response = requests.get(f"{vault_addr}/v1/sys/health", timeout=10)
        
        # Handle Vault-specific status codes
        if response.status_code == 503:  # Sealed
            return True
        if response.status_code in [200, 429, 472, 473]:  # Unsealed or active states
            return False
        if response.status_code == 501:  # Not initialized
            print("Vault is not initialized.")
            return True

        # Unexpected status code
        print(f"Unexpected status code: {response.status_code}")
        return True  # Assume sealed in unknown cases

    except requests.exceptions.RequestException as e:
        # Handle any network-related exceptions or errors
        print(f"Error connecting to Vault server: {e}")
        return True  # Assume sealed if unable to connect