from app.main import app
from app.runtime import get_current_admin, verify_seb
from server import app as legacy_app


def test_api_routes_keep_the_existing_paths_and_methods():
    routes = {}
    for route in app.routes:
        if route.path.startswith("/api/") and hasattr(route, "methods"):
            routes.setdefault(route.path, set()).update(route.methods or ())

    assert routes == {
        "/api/auth/login": {"POST"},
        "/api/auth/me": {"GET"},
        "/api/admin/tokens/generate": {"POST"},
        "/api/admin/tokens": {"GET"},
        "/api/admin/tokens/{token_id}/revoke": {"POST"},
        "/api/admin/tokens/export": {"GET"},
        "/api/admin/questions": {"GET", "POST"},
        "/api/admin/questions/import": {"POST"},
        "/api/admin/questions/{qid}": {"PUT", "DELETE"},
        "/api/admin/disc-items": {"GET", "PUT"},
        "/api/admin/scenario-items": {"GET"},
        "/api/admin/config": {"GET", "PUT"},
        "/api/admin/stats": {"GET"},
        "/api/admin/results": {"GET"},
        "/api/admin/results/export": {"GET"},
        "/api/admin/results/{pid}": {"GET"},
        "/api/exam/seb-status": {"GET"},
        "/api/exam/start": {"POST"},
        "/api/exam/session": {"POST"},
        "/api/exam/answer": {"POST"},
        "/api/exam/tkj/submit": {"POST"},
        "/api/exam/disc/answer": {"POST"},
        "/api/exam/disc/submit": {"POST"},
        "/api/exam/scenario/answer": {"POST"},
        "/api/exam/scenario/submit": {"POST"},
        "/api/exam/work-disc/answer": {"POST"},
        "/api/exam/work-disc/submit": {"POST"},
        "/api/exam/violation": {"POST"},
    }


def test_legacy_server_import_uses_the_same_asgi_app():
    assert legacy_app is app


def test_domain_endpoints_are_implemented_by_their_router_modules():
    endpoints = {
        route.path: route.endpoint.__module__
        for route in app.routes
        if hasattr(route, "endpoint") and route.path.startswith("/api/")
    }

    assert endpoints["/api/auth/login"] == "app.routers.auth"
    assert endpoints["/api/admin/tokens/generate"] == "app.routers.admin"
    assert endpoints["/api/admin/results"] == "app.routers.results"
    assert endpoints["/api/exam/start"] == "app.routers.exam"


def test_auth_and_seb_dependencies_remain_on_protected_routes():
    routes = {
        route.path: route
        for route in app.routes
        if hasattr(route, "dependant") and route.path.startswith("/api/")
    }
    admin_paths = [
        path
        for path in routes
        if path.startswith("/api/admin/")
        and path != "/api/admin/ws/live"
    ]
    assert all(
        any(
            dependency.call is get_current_admin
            for dependency in routes[path].dependant.dependencies
        )
        for path in admin_paths
    )

    seb_paths = [
        "/api/exam/start",
        "/api/exam/session",
        "/api/exam/answer",
        "/api/exam/tkj/submit",
        "/api/exam/disc/answer",
        "/api/exam/disc/submit",
        "/api/exam/scenario/answer",
        "/api/exam/scenario/submit",
        "/api/exam/work-disc/answer",
        "/api/exam/work-disc/submit",
    ]
    assert all(
        any(
            dependency.call is verify_seb
            for dependency in routes[path].dependant.dependencies
        )
        for path in seb_paths
    )


def test_admin_websocket_route_remains_registered():
    assert any(
        getattr(route, "path", None) == "/api/admin/ws/live"
        for route in app.routes
    )
