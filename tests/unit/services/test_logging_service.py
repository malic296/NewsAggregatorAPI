import pytest
from app.handlers import DatabaseLogger, FileLogger
from app.repositories import LoggingRepository
from app.services import LoggingService

def test_db_logging(tmp_path, mocker):
    mocked_repo = mocker.Mock(spec=LoggingRepository)
    service = LoggingService(tmp_path, mocked_repo)
    
    test_log = "TEST_LOG"

    service.log_error_to_db(test_log)

    mocked_repo.log_to_db.assert_called_once_with(test_log)


def test_file_logging(tmp_path, mocker):
    path = tmp_path / "logs.log"
    service = LoggingService(path)

    test_log = "TEST_LOG"

    service.log_error_to_file(test_log)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    assert test_log in content
