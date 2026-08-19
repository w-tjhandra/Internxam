"""SecureCBT Backend regression tests.
Covers: auth, admin CRUD, config, tokens, exam flow, violations auto-submit, SEB toggle.
"""
import os
import time
import pytest
import requests

BASE = os.environ.get("REACT_APP_BACKEND_URL", "https://exam-guard-24.preview.emergentagent.com").rstrip("/")
API = f"{BASE}/api"
ADMIN_EMAIL = "admin@axelbit.com"
ADMIN_PASSWORD = "ax3lb1t"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ---------- Auth ----------
class TestAuth:
    def test_login_success(self):
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data and isinstance(data["access_token"], str)
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "admin"

    def test_login_wrong_password(self):
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"})
        assert r.status_code == 401

    def test_me_authenticated(self, admin_headers):
        r = requests.get(f"{API}/auth/me", headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN_EMAIL

    def test_me_unauthenticated(self):
        r = requests.get(f"{API}/auth/me")
        assert r.status_code == 401


# ---------- Admin: Stats ----------
class TestStats:
    def test_stats(self, admin_headers):
        r = requests.get(f"{API}/admin/stats", headers=admin_headers)
        assert r.status_code == 200
        s = r.json()
        assert "tokens" in s and "questions" in s and "participants" in s


# ---------- Admin: Tokens ----------
class TestTokens:
    def test_generate_list_revoke_export(self, admin_headers):
        r = requests.post(f"{API}/admin/tokens/generate", json={"count": 3}, headers=admin_headers)
        assert r.status_code == 200
        toks = r.json()["tokens"]
        assert len(toks) == 3
        for t in toks:
            assert len(t["code"]) == 8
            assert t["status"] == "unused"

        # list with filter
        r = requests.get(f"{API}/admin/tokens?status=unused", headers=admin_headers)
        assert r.status_code == 200
        codes = [t["code"] for t in r.json()]
        for t in toks:
            assert t["code"] in codes

        # revoke first
        r = requests.post(f"{API}/admin/tokens/{toks[0]['id']}/revoke", headers=admin_headers)
        assert r.status_code == 200

        # revoked cannot revoke again
        r = requests.post(f"{API}/admin/tokens/{toks[0]['id']}/revoke", headers=admin_headers)
        assert r.status_code == 404

        # export csv
        r = requests.get(f"{API}/admin/tokens/export?format=csv", headers=admin_headers)
        assert r.status_code == 200
        assert "Token" in r.text.split("\n")[0]

        # export xlsx
        r = requests.get(f"{API}/admin/tokens/export?format=xlsx", headers=admin_headers)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/vnd.openxml")


# ---------- Admin: Questions ----------
class TestQuestions:
    def test_seed_and_crud(self, admin_headers):
        r = requests.get(f"{API}/admin/questions", headers=admin_headers)
        assert r.status_code == 200
        qs = r.json()
        assert len(qs) >= 27

        payload = {"text": "TEST_Q soal berapa 2+2?", "options": ["3", "4", "5", "6"],
                   "correct_index": 1, "category": "TEST", "difficulty": "mudah"}
        r = requests.post(f"{API}/admin/questions", json=payload, headers=admin_headers)
        assert r.status_code == 200
        q = r.json()
        qid = q["id"]
        assert q["text"] == payload["text"]

        # update
        payload["text"] = "TEST_Q updated"
        r = requests.put(f"{API}/admin/questions/{qid}", json=payload, headers=admin_headers)
        assert r.status_code == 200

        # verify
        r = requests.get(f"{API}/admin/questions", headers=admin_headers)
        found = [x for x in r.json() if x["id"] == qid]
        assert found and found[0]["text"] == "TEST_Q updated"

        # delete
        r = requests.delete(f"{API}/admin/questions/{qid}", headers=admin_headers)
        assert r.status_code == 200

        r = requests.delete(f"{API}/admin/questions/{qid}", headers=admin_headers)
        assert r.status_code == 404

    def test_disc_items_seed(self, admin_headers):
        r = requests.get(f"{API}/admin/disc-items", headers=admin_headers)
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 24
        assert len(items[0]["statements"]) == 4


# ---------- Admin: Config ----------
class TestConfig:
    def test_get_update_config(self, admin_headers):
        r = requests.get(f"{API}/admin/config", headers=admin_headers)
        assert r.status_code == 200
        original = r.json()

        new_cfg = {"tkj_duration_minutes": 45, "disc_duration_minutes": 15,
                   "tkj_question_count": 20, "violation_threshold": 3,
                   "require_seb": False, "seb_browser_exam_key": ""}
        r = requests.put(f"{API}/admin/config", json=new_cfg, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["tkj_duration_minutes"] == 45

        # persist check
        r = requests.get(f"{API}/admin/config", headers=admin_headers)
        assert r.json()["tkj_duration_minutes"] == 45

        # restore
        restore = {k: original[k] for k in new_cfg}
        r = requests.put(f"{API}/admin/config", json=restore, headers=admin_headers)
        assert r.status_code == 200


# ---------- Exam flow ----------
def _fresh_token(admin_headers):
    r = requests.post(f"{API}/admin/tokens/generate", json={"count": 1}, headers=admin_headers)
    return r.json()["tokens"][0]["code"]


class TestExamFlow:
    def test_start_invalid_token(self):
        r = requests.post(f"{API}/exam/start", json={"name": "Test User", "school": "SMK X",
                                                     "class_name": "XI", "token": "XXXXXXXX"})
        assert r.status_code == 404

    def test_full_flow(self, admin_headers):
        code = _fresh_token(admin_headers)
        r = requests.post(f"{API}/exam/start", json={"name": "TEST_Peserta", "school": "SMK Test",
                                                     "class_name": "XI TKJ", "token": code})
        assert r.status_code == 200, r.text
        s = r.json()
        pid = s["participant_id"]
        assert s["stage"] == "tkj"
        assert len(s["questions"]) == s.get("remaining_seconds", 0) and False or len(s["questions"]) >= 20
        assert s["remaining_seconds"] > 0

        # reuse an active token → returns session (not error)
        r2 = requests.post(f"{API}/exam/start", json={"name": "TEST_reuse", "school": "SMK", "class_name": "XI", "token": code})
        assert r2.status_code == 200

        # answer all
        for q in s["questions"]:
            rr = requests.post(f"{API}/exam/answer", json={"participant_id": pid, "token": code,
                                                           "question_id": q["id"], "selected_index": 0})
            assert rr.status_code == 200
            assert rr.json()["saved"] is True

        # session resume
        r = requests.post(f"{API}/exam/session", json={"participant_id": pid, "token": code})
        assert r.status_code == 200
        assert len(r.json()["answers"]) == len(s["questions"])

        # submit TKJ
        r = requests.post(f"{API}/exam/tkj/submit", json={"participant_id": pid, "token": code})
        assert r.status_code == 200
        st = r.json()
        assert st["stage"] == "disc"
        assert len(st["disc_items"]) == 24

        # answer DISC 24
        for i in range(24):
            rr = requests.post(f"{API}/exam/disc/answer", json={"participant_id": pid, "token": code,
                                                                "group_index": i, "most": 0, "least": 1})
            assert rr.status_code == 200

        # most == least → 400
        rr = requests.post(f"{API}/exam/disc/answer", json={"participant_id": pid, "token": code,
                                                            "group_index": 0, "most": 2, "least": 2})
        assert rr.status_code == 400

        # submit disc
        r = requests.post(f"{API}/exam/disc/submit", json={"participant_id": pid, "token": code})
        assert r.status_code == 200
        assert r.json()["stage"] == "done"

        # token completed → reuse denied
        r = requests.post(f"{API}/exam/start", json={"name": "TEST_reuse2", "school": "SMK", "class_name": "XI", "token": code})
        assert r.status_code == 403

    def test_violations_auto_submit(self, admin_headers):
        code = _fresh_token(admin_headers)
        r = requests.post(f"{API}/exam/start", json={"name": "TEST_Violator", "school": "SMK",
                                                     "class_name": "XI", "token": code})
        assert r.status_code == 200
        pid = r.json()["participant_id"]

        for i in range(2):
            rr = requests.post(f"{API}/exam/violation", json={"participant_id": pid, "token": code,
                                                              "violation_type": "tab-switch", "detail": ""})
            assert rr.status_code == 200
            assert rr.json()["auto_submitted"] is False

        rr = requests.post(f"{API}/exam/violation", json={"participant_id": pid, "token": code,
                                                          "violation_type": "tab-switch", "detail": ""})
        assert rr.status_code == 200
        body = rr.json()
        assert body["auto_submitted"] is True
        assert body["stage"] == "done"

        # verify participant status
        r = requests.get(f"{API}/admin/results", headers={"Authorization": f"Bearer {_admin_token_cache()}"})
        found = [p for p in r.json() if p["id"] == pid]
        assert found and found[0]["stage"] == "done" and found[0]["auto_submitted"] is True


_cached_token = {}
def _admin_token_cache():
    if "t" not in _cached_token:
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        _cached_token["t"] = r.json()["access_token"]
    return _cached_token["t"]


# ---------- Admin results ----------
class TestResults:
    def test_results_list_and_export(self, admin_headers):
        r = requests.get(f"{API}/admin/results", headers=admin_headers)
        assert r.status_code == 200
        results = r.json()

        r = requests.get(f"{API}/admin/results/export?format=csv", headers=admin_headers)
        assert r.status_code == 200

        r = requests.get(f"{API}/admin/results/export?format=xlsx", headers=admin_headers)
        assert r.status_code == 200

        if results:
            pid = results[0]["id"]
            r = requests.get(f"{API}/admin/results/{pid}", headers=admin_headers)
            assert r.status_code == 200
            d = r.json()
            assert "violations" in d


# ---------- SEB toggle ----------
class TestSEB:
    def test_seb_gating(self, admin_headers):
        # get original
        orig = requests.get(f"{API}/admin/config", headers=admin_headers).json()
        # enable
        cfg = {k: orig[k] for k in ["tkj_duration_minutes", "disc_duration_minutes",
                                     "tkj_question_count", "violation_threshold",
                                     "require_seb", "seb_browser_exam_key"]}
        cfg["require_seb"] = True
        cfg["seb_browser_exam_key"] = ""
        r = requests.put(f"{API}/admin/config", json=cfg, headers=admin_headers)
        assert r.status_code == 200

        try:
            code = _fresh_token(admin_headers)
            # without SEB header → 403
            r = requests.post(f"{API}/exam/start", json={"name": "TEST_seb", "school": "SMK",
                                                         "class_name": "XI", "token": code})
            assert r.status_code == 403

            # with SEB header (BEK empty → any hash passes)
            r = requests.post(f"{API}/exam/start",
                              json={"name": "TEST_seb", "school": "SMK", "class_name": "XI", "token": code},
                              headers={"X-SafeExamBrowser-ConfigKeyHash": "deadbeef"})
            assert r.status_code == 200
        finally:
            # restore
            cfg["require_seb"] = False
            requests.put(f"{API}/admin/config", json=cfg, headers=admin_headers)
