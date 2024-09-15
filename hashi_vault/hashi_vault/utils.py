import time
import requests

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