import pytest
import requests
from hashi_vault.utils import is_sealed

def test_is_sealed_true(requests_mock):
    # Mock the Vault API response for sealed=True
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", json={"sealed": True})

    # Test the function
    assert is_sealed(vault_addr) is True

def test_is_sealed_false(requests_mock):
    # Mock the Vault API response for sealed=False
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", json={"sealed": False})

    # Test the function
    assert is_sealed(vault_addr) is False

def test_is_sealed_connection_error(requests_mock):
    # Simulate a connection error
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", exc=requests.exceptions.ConnectionError)

    # Test the function
    assert is_sealed(vault_addr) is True

def test_is_sealed_timeout_error(requests_mock):
    # Simulate a timeout error
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", exc=requests.exceptions.Timeout)

    # Test the function
    assert is_sealed(vault_addr) is True

def test_is_sealed_invalid_json(requests_mock):
    # Simulate an invalid JSON response
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", text="Invalid JSON")

    # Test the function
    assert is_sealed(vault_addr) is True