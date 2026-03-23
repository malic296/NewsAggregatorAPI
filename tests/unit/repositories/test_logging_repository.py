import pytest
from app.models import DBResult

def test_log_to_db_success(logging_repository, mocker):
    db_result = DBResult(True, None, None, row_count=1)
    mocker.patch.object(logging_repository, "_execute", return_value=db_result)
    logging_repository.log_to_db("")

def test_log_to_db_error(logging_repository, mocker, invalid_db_result):
    mocker.patch.object(logging_repository, "_execute", return_value=invalid_db_result)

    with pytest.raises(Exception) as e:
        logging_repository.log_to_db("")

    assert str(e.value) == "INVALID_DB_RESULT_MESSAGE"

def test_log_to_db_invalid_row_count(logging_repository, mocker):
    db_result = DBResult(True, None, None, row_count=0)
    mocker.patch.object(logging_repository, "_execute", return_value=db_result)

    with pytest.raises(Exception) as e:
        logging_repository.log_to_db("")

    assert str(e.value) == "log_to_db method did not update any rows."