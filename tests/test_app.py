"""Tests for the Portainer template proxy server."""
import json
import pytest
from unittest.mock import patch, Mock
from app import app, validate_url


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- Health Check Tests ---

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['status'] == 'ok'


# --- URL Validation Tests ---

def test_validate_url_https():
    valid, err = validate_url('https://example.com/templates.json')
    assert valid is True
    assert err is None


def test_validate_url_http_rejected():
    valid, err = validate_url('http://example.com/templates.json')
    assert valid is False
    assert 'HTTPS' in err


def test_validate_url_empty():
    valid, err = validate_url('')
    assert valid is False


def test_validate_url_no_scheme():
    valid, err = validate_url('example.com/templates.json')
    assert valid is False


# --- Missing Parameters Tests ---

def test_missing_all_params(client):
    rv = client.get('/modify')
    assert rv.status_code == 400


def test_missing_domain_param(client):
    rv = client.get('/modify?portainer_template_url=https://example.com/t.json')
    assert rv.status_code == 400


def test_missing_url_param(client):
    rv = client.get('/modify?TRAEFIK_INGRESS_DOMAIN=lab.example.com')
    assert rv.status_code == 400


def test_http_url_rejected(client):
    rv = client.get('/modify?portainer_template_url=http://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=lab.example.com')
    assert rv.status_code == 400
    data = json.loads(rv.data)
    assert 'HTTPS' in data['error']


# --- Successful Substitution Tests ---

@patch('app.requests.get')
def test_successful_substitution(mock_get, client):
    mock_response = Mock()
    mock_response.text = '{"domain": "${TRAEFIK_INGRESS_DOMAIN}", "other": "{$CUSTOM}"}'
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    rv = client.get('/modify?portainer_template_url=https://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=lab.example.com&CUSTOM=myval')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['domain'] == 'lab.example.com'
    assert data['other'] == 'myval'


@patch('app.requests.get')
def test_dollar_brace_substitution(mock_get, client):
    mock_response = Mock()
    mock_response.text = '{"host": "{$TRAEFIK_INGRESS_DOMAIN}"}'
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    rv = client.get('/modify?portainer_template_url=https://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=test.com')
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data['host'] == 'test.com'


@patch('app.requests.get')
def test_content_type_json(mock_get, client):
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    rv = client.get('/modify?portainer_template_url=https://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=x.com')
    assert rv.content_type == 'application/json'


# --- Error Handling Tests ---

@patch('app.requests.get')
def test_upstream_error(mock_get, client):
    mock_get.side_effect = Exception("Connection refused")

    rv = client.get('/modify?portainer_template_url=https://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=x.com')
    assert rv.status_code == 500


@patch('app.requests.get')
def test_upstream_timeout(mock_get, client):
    import requests as req
    mock_get.side_effect = req.Timeout("timed out")

    rv = client.get('/modify?portainer_template_url=https://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=x.com')
    assert rv.status_code == 504


@patch('app.requests.get')
def test_request_has_timeout(mock_get, client):
    mock_response = Mock()
    mock_response.text = '{}'
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    client.get('/modify?portainer_template_url=https://example.com/t.json&TRAEFIK_INGRESS_DOMAIN=x.com')
    _, kwargs = mock_get.call_args
    assert 'timeout' in kwargs
    assert kwargs['timeout'] > 0
