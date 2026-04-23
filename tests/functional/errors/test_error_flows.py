from app.core.errors import ArticleNotFoundError


def test_not_authorized(client):
    assert client.get("/v1/articles/").status_code == 401
    assert client.get("/v1/channels/").status_code == 401
    assert client.get("/v1/consumers/me").status_code == 401
    assert client.post("/v1/articles/article-uuid/like").status_code == 401


def test_invalid_article_uuid(client, auth_headers, functional_services):
    functional_services.article_service.like_article.side_effect = ArticleNotFoundError()

    response = client.post("/v1/articles/missing-uuid/like", headers=auth_headers)
    json_response = response.json()

    assert response.status_code == 404
    assert json_response == {"success": False, "message": "Article not found."}


def test_rate_limit_exceeded(client, auth_headers, functional_services):
    functional_services.cache_service.can_request_go_through.return_value = False

    response = client.get("/v1/articles/", headers=auth_headers)
    json_response = response.json()

    assert response.status_code == 429
    assert json_response == {
        "success": False,
        "message": "Too many requests. Try again in a short moment.",
    }
