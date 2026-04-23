import pytest

from app.core.errors import DatabaseError, MappingError
from app.models import DBResult


def test_get_articles_success(mocker, article_repository, db_result_article, consumer):
    mocker.patch.object(article_repository, "_execute", return_value=db_result_article)

    articles = article_repository.get_articles(consumer=consumer, hours=3)

    assert len(articles) == 1
    assert articles[0].uuid == db_result_article.data[0]["uuid"]


def test_get_articles_failure(mocker, article_repository, consumer):
    mocker.patch.object(article_repository, "_execute", return_value=DBResult(success=False, error_message="db failed"))

    with pytest.raises(DatabaseError) as exc:
        article_repository.get_articles(consumer=consumer, hours=3)

    assert exc.value.internal_message == "Query execution failed for method: get_articles. Error message: db failed"


def test_get_article_missing_returns_none(mocker, article_repository):
    mocker.patch.object(article_repository, "_execute", return_value=DBResult(success=True, data=[], row_count=0))

    assert article_repository.get_article("missing") is None


def test_article_uuid_to_id_mapping_error(mocker, article_repository):
    mocker.patch.object(
        article_repository,
        "_execute",
        return_value=DBResult(success=True, data=[{"wrong_key": 1}], row_count=1),
    )

    with pytest.raises(MappingError) as exc:
        article_repository.article_uuid_to_id("article-uuid")

    assert "article_uuid_to_id" in exc.value.internal_message


def test_like_article_insert_branch(mocker, article_repository):
    mocker.patch.object(
        article_repository,
        "_execute",
        side_effect=[
            DBResult(success=True, data=[], row_count=0),
            DBResult(success=True, data=None, row_count=1),
        ],
    )

    assert article_repository.like_article(article_id=1, consumer_id=1) is True


def test_like_article_delete_branch(mocker, article_repository):
    mocker.patch.object(
        article_repository,
        "_execute",
        side_effect=[
            DBResult(success=True, data=[{"exists": 1}], row_count=1),
            DBResult(success=True, data=None, row_count=1),
        ],
    )

    assert article_repository.like_article(article_id=1, consumer_id=1) is False


def test_like_article_raises_when_no_row_changed(mocker, article_repository):
    mocker.patch.object(
        article_repository,
        "_execute",
        side_effect=[
            DBResult(success=True, data=[], row_count=0),
            DBResult(success=True, data=None, row_count=0),
        ],
    )

    with pytest.raises(DatabaseError) as exc:
        article_repository.like_article(article_id=1, consumer_id=1)

    assert "No rows were changed when liking an article." in exc.value.internal_message
