import pytest
import requests
from hashi_vault.utils  import is_sealed

def test_is_sealed_503_sealed(requests_mock):
    # Mock the Vault API response for sealed (503)
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", status_code=503)

    # Test the function
    assert is_sealed(vault_addr) is True

def test_is_sealed_200_unsealed(requests_mock):
    # Mock the Vault API response for unsealed (200)
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", status_code=200)

    # Test the function
    assert is_sealed(vault_addr) is False

def test_is_sealed_429_standby(requests_mock):
    # Mock the Vault API response for standby (429)
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", status_code=429)

    # Test the function
    assert is_sealed(vault_addr) is False

def test_is_sealed_501_not_initialized(requests_mock):
    # Mock the Vault API response for not initialized (501)
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", status_code=501)

    # Test the function
    assert is_sealed(vault_addr) is True

def test_is_sealed_unexpected_status_code(requests_mock):
    # Mock the Vault API response for an unexpected status code (400)
    vault_addr = "https://vault.example.com"
    requests_mock.get(f"{vault_addr}/v1/sys/health", status_code=400)

    # Test the function
    assert is_sealed(vault_addr) is True  # Assume sealed in unexpected cases

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