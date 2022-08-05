#!/usr/bin/python

"""This file is part of Teamlock.
Teamlock is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Teamlock is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Teamlock.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Olivier de Régis"
__credits__ = []
__license__ = "GPLv3"
__version__ = "3.0.0"
__maintainer__ = "Teamlock Project"
__email__ = "contact@teamlock.io"
__doc__ = ''

from toolkits.mongo import connect_to_database
from mongoengine.connection import get_db
from fastapi.testclient import TestClient
from . import variables
from main import app
import pytest

client = TestClient(app)

DATABASE_NAME: str = "teamlock_test"


@pytest.fixture(scope="session", autouse=True)
def init():
    connect_to_database(database_name=DATABASE_NAME)
    yield None
    get_db().client.drop_database(DATABASE_NAME)


def test_install():
    response = client.post("/install", json=variables.INSTALL_PARAMS)
    user_id: str = response.text.replace('"', '')

    url: str = f"/api/v1/user/configure/{user_id}"
    params: dict = {
        "password": variables.PASSWORD,
        "confirm_password": variables.PASSWORD
    }

    response = client.post(url, json=params)
    assert response.status_code == 202


def test_login():
    headers: dict = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = client.post(
        "/api/v1/auth/token",
        variables.LOGIN_PARAMS,
        headers=headers
    )

    assert response.status_code == 200
    pytest.token = response.json()["access_token"]


def test_get_workspaces():
    client.headers["Authorization"] = f"Bearer {pytest.token}"
    response = client.get("/api/v1/workspace")
    assert response.status_code == 200

    data = response.json()[0]
    assert data["name"] == "Personal"


def test_create_workspace():
    response = client.post(
        "/api/v1/workspace/",
        json=variables.CREATE_WORKSPACE_PARAMS
    )

    assert response.status_code == 201
    pytest.workspace_id = response.text


def test_get_folders():
    response = client.get(f"/api/v1/workspace/{pytest.workspace_id}/folders")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_folder():
    params: dict = variables.CREATE_FOLDER_PARAMS
    params["workspace"] = pytest.workspace_id

    response = client.post("/api/v1/folder/", json=params)
    assert response.status_code == 201
    pytest.folder_id = response.text


def test_create_key():
    params: dict = variables.CREATE_KEY_PARAMS
    params["folder"] = pytest.folder_id

    response = client.post("/api/v1/secret/", json=params)
    assert response.status_code == 201
    pytest.secret_id = response.text


def test_get_keys():
    response = client.get(f"/api/v1/folder/{pytest.folder_id}/keys")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    key = data[0]
    for k in ("informations", "name", "url", "login", "ip"):
        assert key[k] == variables.CREATE_KEY_PARAMS[k]
    
    pytest.key = key


def test_get_password():
    response = client.get(f"/api/v1/secret/{pytest.key['_id']}")
    assert response.status_code == 200
    data = response.json()

    for k in ("informations", "name", "url", "login", "ip", "password"):
        assert data[k]["value"] == variables.CREATE_KEY_PARAMS[k]["value"]
    
    pytest.key = data


def test_update_key():
    params: dict = pytest.key
    params["name"] = {
        "encryption": True,
        "value": "update"
    }

    response = client.put(f"/api/v1/secret/{pytest.key['_id']}", json=params)
    assert response.status_code == 202


def test_delete_key():
    response = client.delete(f"/api/v1/secret/{pytest.key['_id']}")
    assert response.status_code == 204
    