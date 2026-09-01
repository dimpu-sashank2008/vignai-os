import os
import pytest
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_frontend_index_html_opengraph_metadata():
    """Verify that frontend/index.html includes all required OpenGraph and SEO metadata."""
    index_html_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../frontend/index.html")
    )
    assert os.path.exists(index_html_path), "frontend/index.html not found"

    with open(index_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    assert '<meta property="og:title"' in html_content
    assert '<meta property="og:description"' in html_content
    assert '<meta property="og:type"' in html_content
    assert '<meta name="twitter:card"' in html_content
    assert '<meta name="description"' in html_content
    assert '<meta name="theme-color"' in html_content

def test_api_does_not_set_non_essential_tracking_cookies(client):
    """Verify that the application uses purely JWT Bearer / localStorage and zero tracking cookies."""
    response = client.post(
        "/api/auth/login",
        json={"identifier": "student", "password": "password123"}
    )
    assert response.status_code == 200
    cookies = response.cookies
    assert "tracking_id" not in cookies
    assert "_ga" not in cookies
    assert "_fbp" not in cookies
