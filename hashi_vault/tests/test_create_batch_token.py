import pytest
import requests
from requests.exceptions import HTTPError
from unittest.mock import patch
from hashi_vault.utils import create_batch_token


def test_create_batch_token_success(requests_mock):
    vault_addr = "vault-server"
    access_token = "sometoken"
    ttl = 3600
    policies = ["default"]
    new_token = "newbatchtoken"
    response_data = {"auth": {"client_token": new_token}}

    requests_mock.post(
        f"https://{vault_addr}/v1/auth/token/create-orphan", json=response_data
    )

    result = create_batch_token(vault_addr, access_token, ttl, policies)
    assert result == new_token


def test_create_batch_token_http_error(requests_mock):
    vault_addr = "vault-server"
    access_token = "sometoken"
    ttl = 3600
    policies = ["default"]

    requests_mock.post(
        f"https://{vault_addr}/v1/auth/token/create-orphan", status_code=400
    )

    result = create_batch_token(vault_addr, access_token, ttl, policies)
    assert result is None


def test_create_batch_token_general_exception(requests_mock):
    vault_addr = "vault-server"
    access_token = "sometoken"
    ttl = 3600
    policies = ["default"]

    requests_mock.post(
        f"https://{vault_addr}/v1/auth/token/create-orphan",
        exc=Exception("General error"),
    )

    result = create_batch_token(vault_addr, access_token, ttl, policies)
    assert result is None
