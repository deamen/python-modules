import pytest
import requests
import requests_mock
from hashi_vault.utils import get_leader, ActiveNodeNotFoundError  # Replace 'your_module' with the actual module name

# Test successful leader node retrieval
def test_get_leader_success():
    servers = ["http://vault-server1:8200", "http://vault-server2:8200"]
    
    with requests_mock.Mocker() as mocker:
        mocker.get("http://vault-server1:8200/v1/sys/leader", json={"leader_address": "https://127.0.0.1:8200"})
        leader_node = get_leader(servers)
        
    assert leader_node == "https://127.0.0.1:8200"

# Test when the first server fails, but the second one returns a leader
def test_get_leader_retry_success():
    servers = ["http://vault-server1:8200", "http://vault-server2:8200"]
    
    with requests_mock.Mocker() as mocker:
        mocker.get("http://vault-server1:8200/v1/sys/leader", status_code=500)  # Simulate failure
        mocker.get("http://vault-server2:8200/v1/sys/leader", json={"leader_address": "https://127.0.0.2:8200"})
        
        leader_node = get_leader(servers)
    
    assert leader_node == "https://127.0.0.2:8200"

# Test when no leader is found on any server, raising ActiveNodeNotFoundError
def test_get_leader_not_found():
    servers = ["http://vault-server1:8200", "http://vault-server2:8200"]
    
    with requests_mock.Mocker() as mocker:
        mocker.get("http://vault-server1:8200/v1/sys/leader", json={})
        mocker.get("http://vault-server2:8200/v1/sys/leader", json={})
        
        with pytest.raises(ActiveNodeNotFoundError):
            get_leader(servers)

# Test when a request fails due to a connection error
def test_get_leader_connection_error():
    servers = ["http://vault-server1:8200", "http://vault-server2:8200"]
    
    with requests_mock.Mocker() as mocker:
        mocker.get("http://vault-server1:8200/v1/sys/leader", exc=requests.exceptions.ConnectionError)
        mocker.get("http://vault-server2:8200/v1/sys/leader", json={"leader_address": "https://127.0.0.2:8200"})
        
        leader_node = get_leader(servers)
    
    assert leader_node == "https://127.0.0.2:8200"