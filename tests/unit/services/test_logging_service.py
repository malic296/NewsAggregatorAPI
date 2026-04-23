import pytest

from app.services import LoggingService


def test_db_logging(tmp_path, mocker):
    repository = mocker.Mock()
    service = LoggingService(tmp_path / "logs.log", repository)

    service.log_error_to_db("TEST_LOG")

    repository.log_to_db.assert_called_once_with("TEST_LOG")


def test_db_logging_without_repository(tmp_path):
    service = LoggingService(tmp_path / "logs.log")

    with pytest.raises(Exception, match="Logging repository init failed."):
        service.log_error_to_db("TEST_LOG")


def test_file_logging(tmp_path):
    path = tmp_path / "logs.log"
    service = LoggingService(path)

    service.log_error_to_file("TEST_LOG")

    assert "TEST_LOG" in path.read_text(encoding="utf-8")
