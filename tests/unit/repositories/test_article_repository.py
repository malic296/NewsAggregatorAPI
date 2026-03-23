from app.core.errors import InternalError
from app.models import Consumer, Article, DBResult
import pytest

def test_get_articles_success(mocker, article_repository, db_result_articles):
    mocker.patch.object(article_repository, '_execute', return_value=db_result_articles)

    articles: list[Article] = article_repository.get_articles(Consumer(1, "1", "consumer", "email"), [1, 2], 3)
    assert len(articles) == len(db_result_articles.data)
    assert articles == [Article(**article) for article in db_result_articles.data]

def test_get_articles_fail(mocker, article_repository, invalid_db_result):
    mocker.patch.object(article_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        article_repository.get_articles(Consumer(1, "1", "consumer", "email"), [1, 2], 3)

    assert str(e.value) == "Failed getting articles with get_articles method because: " + invalid_db_result.error_message

def test_get_articles_invalid_format(mocker, article_repository, db_result_articles):
    db_result_articles.data = [{k: v for k, v in article.items() if k != "uuid"} for article in db_result_articles.data]
    mocker.patch.object(article_repository, '_execute', return_value= db_result_articles)

    with pytest.raises(InternalError) as e:
        article_repository.get_articles(Consumer(1, "1", "consumer", "email"), [1, 2], 3)

    assert "uuid" in str(e.value)


def test_article_uuid_to_id_success(mocker, article_repository, db_result_id):
    mocker.patch.object(article_repository, '_execute', return_value=db_result_id)

    id: int = article_repository.article_uuid_to_id("1")
    assert id == db_result_id.data[0]["id"]

def test_article_uuid_to_id_fail(mocker, article_repository, invalid_db_result):
    mocker.patch.object(article_repository, '_execute', return_value=invalid_db_result)

    with pytest.raises(InternalError) as e:
        article_repository.article_uuid_to_id("1")

    assert str(e.value) == "Query created by article_uuid_to_id failed because: " + invalid_db_result.error_message

def test_article_uuid_to_id_invalid_format(mocker, article_repository, db_result_articles):
    db_result_articles.data = [{k: v for k, v in article.items() if k != "id"} for article in db_result_articles.data]
    mocker.patch.object(article_repository, '_execute', return_value= db_result_articles)

    with pytest.raises(InternalError) as e:
        article_repository.article_uuid_to_id("1")

    assert "id" in str(e.value)

def test_like_article_success(mocker, article_repository):
    mocker.patch.object(article_repository, '_execute', return_value=DBResult(True, None, None, 1))

    result: bool = article_repository.like_article(1, 1)
    assert result == True

@pytest.mark.parametrize(
    "db_result, error_message",
    [
        (DBResult(True, None, None, row_count=0), "Method like_article did not change any rows."),
        (DBResult(False, "NONE", None, row_count=0), "Method like_article failed initial select because: NONE."),
    ]
)
def test_like_article_fail(mocker, article_repository, db_result, error_message):
    mocker.patch.object(article_repository, '_execute', return_value=db_result)

    with pytest.raises(InternalError) as e:
        article_repository.like_article(1, 1)

    assert str(e.value) == error_message