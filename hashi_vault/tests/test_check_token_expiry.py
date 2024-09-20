import pytest
import requests
from requests.exceptions import RequestException
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from hashi_vault.utils import check_token_expiry


def test_check_token_expiry_not_expiring_soon(requests_mock):
    vault_addr = "http://vault-server"
    vault_token = "sometoken"
    days_left = 10
    expire_time = (datetime.now(timezone.utc) + timedelta(days=20)).isoformat()
    token_response = {"data": {"expire_time": expire_time}}
    requests_mock.get(f"{vault_addr}/v1/auth/token/lookup-self", json=token_response)

    will_expire, actual_days_left = check_token_expiry(vault_addr, vault_token, days_left)
    
    assert will_expire is False
    assert actual_days_left == pytest.approx(20, abs=1)  # Allow a margin of 1 day


def test_check_token_expiry_expiring_soon(requests_mock):
    vault_addr = "http://vault-server"
    vault_token = "sometoken"
    days_left = 10
    expire_time = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    token_response = {"data": {"expire_time": expire_time}}
    requests_mock.get(f"{vault_addr}/v1/auth/token/lookup-self", json=token_response)

    will_expire, actual_days_left = check_token_expiry(vault_addr, vault_token, days_left)
    
    assert will_expire is True
    assert actual_days_left == pytest.approx(5, abs=1)  # Allow a margin of 1 day


def test_check_token_expiry_no_expiration_time(requests_mock):
    vault_addr = "http://vault-server"
    vault_token = "sometoken"
    days_left = 10
    token_response = {"data": {}}
    requests_mock.get(f"{vault_addr}/v1/auth/token/lookup-self", json=token_response)

    will_expire, actual_days_left = check_token_expiry(vault_addr, vault_token, days_left)
    
    assert will_expire is False
    assert actual_days_left == -1


def test_check_token_expiry_server_unreachable(requests_mock):
    vault_addr = "http://vault-server"
    vault_token = "sometoken"
    days_left = 10
    requests_mock.get(
        f"{vault_addr}/v1/auth/token/lookup-self",
        exc=RequestException("Server not reachable"),
    )

    will_expire, actual_days_left = check_token_expiry(vault_addr, vault_token, days_left)
    
    assert will_expire is True
    assert actual_days_left is None
