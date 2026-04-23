import pytest

from app.models import DBResult


def test_log_to_db_success(logging_repository, log_record, mocker):
    mocker.patch.object(logging_repository, "_execute", return_value=DBResult(success=True, data=None, row_count=1))

    logging_repository.log_to_db(log_record)


def test_log_to_db_error(logging_repository, log_record, mocker):
    mocker.patch.object(logging_repository, "_execute", return_value=DBResult(success=False, error_message="db failed"))

    with pytest.raises(Exception, match="db failed"):
        logging_repository.log_to_db(log_record)


def test_log_to_db_invalid_row_count(logging_repository, log_record, mocker):
    mocker.patch.object(logging_repository, "_execute", return_value=DBResult(success=True, data=None, row_count=0))

    with pytest.raises(Exception, match="did not update any rows"):
        logging_repository.log_to_db(log_record)
