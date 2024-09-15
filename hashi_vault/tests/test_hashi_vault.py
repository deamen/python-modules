import pytest
import requests
from requests.exceptions import RequestException
from unittest.mock import patch
from hashi_vault.utils import get_active_node, ActiveNodeNotFoundError

def test_get_active_node_success(requests_mock):
    servers = ["http://server1", "http://server2"]
    active_node_response = {
        "Nodes": [
            {"active_node": False, "api_address": "http://server1"},
            {"active_node": True, "api_address": "http://server2"}
        ]
    }
    requests_mock.get("http://server1/v1/sys/ha-status", json=active_node_response)
    requests_mock.get("http://server2/v1/sys/ha-status", json=active_node_response)

    active_node = get_active_node(servers)
    assert active_node == "http://server2"

def test_get_active_node_no_active_node(requests_mock):
    servers = ["http://server1", "http://server2"]
    no_active_node_response = {
        "Nodes": [
            {"active_node": False, "api_address": "http://server1"},
            {"active_node": False, "api_address": "http://server2"}
        ]
    }
    requests_mock.get("http://server1/v1/sys/ha-status", json=no_active_node_response)
    requests_mock.get("http://server2/v1/sys/ha-status", json=no_active_node_response)

    with pytest.raises(ActiveNodeNotFoundError):
        get_active_node(servers)

def test_get_active_node_server_unreachable(requests_mock):
    servers = ["http://server1", "http://server2"]
    requests_mock.get("http://server1/v1/sys/ha-status", exc=RequestException("Server not reachable"))
    requests_mock.get("http://server2/v1/sys/ha-status", exc=RequestException("Server not reachable"))

    with pytest.raises(ActiveNodeNotFoundError):
        get_active_node(servers)

@patch("time.sleep", return_value=None)
def test_get_active_node_retries(mock_sleep, requests_mock):
    servers = ["http://server1"]
    response = {
        "Nodes": [
            {"active_node": False, "api_address": "http://server1"}
        ]
    }
    requests_mock.get("http://server1/v1/sys/ha-status", exc=RequestException("Server not reachable"))
    requests_mock.get("http://server1/v1/sys/ha-status", json=response)

    with pytest.raises(ActiveNodeNotFoundError):
        get_active_node(servers, retries=2, interval=1)

    assert mock_sleep.call_count == 1

def test_get_active_node_no_servers():
    servers = []
    with pytest.raises(ActiveNodeNotFoundError):
        get_active_node(servers)