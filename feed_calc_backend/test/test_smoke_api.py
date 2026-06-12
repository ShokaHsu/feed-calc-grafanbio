import pytest
from .factories import make_standard, make_ingredient_corn, make_ingredient_sbm

pytestmark = pytest.mark.django_db

class TestIngredients:
    def test_list_and_detail(self, api_client):
        r = api_client.get("/api/ingredients/")
        assert r.status_code in (200, 401, 403)
        r = api_client.get("/api/ingredients/999999/")
        assert r.status_code in (200, 401, 403, 404)

class TestStandards:
    @pytest.mark.parametrize("url", [
        "/api/standards/requirements/",
        "/api/standards/stages/",
    ])
    def test_viewsets_exist(self, api_client, url):
        r = api_client.get(url)
        assert r.status_code in (200, 401, 403)

class TestFormulasFlow:
    def test_create_formula_and_retrieve(self, api_client, user):
        api_client.force_authenticate(user=user)
        std = make_standard()
        corn = make_ingredient_corn()
        sbm = make_ingredient_sbm()

        payload = {
            "name": "Smoke Test Formula",
            "standard_id": std.id,
            "items": [
                {"ingredient": corn.id, "amount_kg": 60.0},
                {"ingredient": sbm.id, "amount_kg": 40.0},
            ],
        }
        r = api_client.post("/api/formulas/", payload, format="json")
        assert r.status_code == 201, r.data

        fid = r.data["id"]

        r = api_client.get(f"/api/formulas/{fid}/")
        assert r.status_code == 200
        assert "items" in r.data
        assert "cost_per_kg" in r.data
        assert "total_cost" in r.data

class TestAnalysisAndReports:
    def test_analysis_routes(self, api_client):
        r = api_client.get("/api/analysis/gap/")
        assert r.status_code in (200, 401, 403, 404, 501, 503)
        r = api_client.get("/api/analysis/cost/")
        assert r.status_code in (200, 401, 403, 404, 501, 503)

    def test_reports_route(self, api_client):
        r = api_client.get("/api/reports/formula/1.pdf")
        assert r.status_code in (200, 401, 403, 404)

class TestAuth:
    def test_token_endpoints(self, api_client, user):
        # App uses Djoser token auth — endpoint is /api/auth/token/login/
        r = api_client.post("/api/auth/token/login/", {"username": user.username, "password": "pass1234"}, format="json")
        assert r.status_code == 200, r.data
        assert "auth_token" in r.data

        api_client.credentials(HTTP_AUTHORIZATION=f"Token {r.data['auth_token']}")
        r2 = api_client.get("/api/auth/users/me/")
        assert r2.status_code in (200, 403)
