from typing import Dict

import pytest
from fastapi.testclient import TestClient
from service import app


def calculate(data: Dict):
    client = TestClient(app)
    return client.post('/api/calculate/', json=data)


def test_api_calculate_invalid_state():
    resp = calculate({'state': 'NY', 'price': 1000, 'count': 200})

    assert resp.status_code == 422
    assert "value is not a valid enumeration member; permitted: 'UT', 'NV', 'TX', 'AL', 'CA'" in resp.text


def test_api_calculate_invalid_price():
    resp = calculate({'state': 'TX', 'price': -100, 'count': 200})

    assert resp.status_code == 422
    assert 'ensure this value is greater than 0' in resp.text


def test_api_calculate_invalid_count():
    resp = calculate({'state': 'TX', 'price': 1000, 'count': 0})

    assert resp.status_code == 422
    assert 'ensure this value is greater than 0' in resp.text


def test_api_calculate_without_discount():
    resp = calculate({'state': 'TX', 'price': 10, 'count': 10})

    assert resp.status_code == 200
    assert resp.json() == {'total_amount': 106.25}


def test_api_calculate_with_discount_eq():
    resp = calculate({'state': 'TX', 'price': 100, 'count': 10})

    # discounted: 1000 - 30 = 970
    # tax: 970 / 100 * 6.25 (TX) = 60.62

    assert resp.status_code == 200
    assert resp.json() == {'total_amount': 1030.62}


def test_api_calculate_with_discount_lt():
    resp = calculate({'state': 'TX', 'price': 499.99, 'count': 10})

    # discounted: 4999.9 - 149.99 = 4849.90
    # tax: = 4849.90 / 100 * 6.25 = 303.118

    assert resp.status_code == 200
    assert resp.json() == {'total_amount': 5153.02}


def test_api_calculate_with_discount_gt():
    resp = calculate({'state': 'TX', 'price': 500, 'count': 10})

    # discounted: 5000 - 250 = 4750
    # tax: = 4750 / 100 * 6.25 = 296.875

    assert resp.status_code == 200
    assert resp.json() == {'total_amount': 5046.88}


@pytest.mark.parametrize('state_r', [
    ('TX', 5046.88), ('UT', 5075.38), ('NV', 5130.0), ('AL', 4940.0), ('CA', 5141.88)])
def test_api_calculate_all_with_discount(state_r):
    state, total_amount = state_r

    resp = calculate({'state': state, 'price': 500, 'count': 10})

    assert resp.status_code == 200
    assert resp.json() == {'total_amount': total_amount}


@pytest.mark.parametrize('state_r', [
    ('TX', 106.25), ('UT', 106.85), ('NV', 108.0), ('AL', 104.0), ('CA', 108.25)])
def test_api_calculator_all_without_discount(state_r):
    state, total_amount = state_r

    resp = calculate({'state': state, 'price': 10, 'count': 10})

    assert resp.status_code == 200
    assert resp.json() == {'total_amount': total_amount}
