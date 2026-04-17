from app.handlers import create_logging_handler
from app.repositories import LoggingRepository

def test_logging_handler(tmp_path, mocker):
    path = tmp_path / "logs.log"
    repository = LoggingRepository()
    mocker.patch.object(repository, "log_to_db", side_effect=Exception("EXCEPTION"))
    logging_handler = create_logging_handler(path=path, repo=repository)
    test_log = "TEST_LOG"
    logging_handler.handle(test_log)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        assert test_log in content