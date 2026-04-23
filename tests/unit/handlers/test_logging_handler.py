import logging

from app.core.logger.handlers import DatabaseHandler, DropOnFailHandler


def test_database_handler_emits_record(log_record):
    calls = []
    handler = DatabaseHandler(writer_func=calls.append)

    handler.emit(log_record)

    assert calls == [log_record]


def test_drop_on_fail_handler_removes_itself(mocker, log_record):
    logger = logging.getLogger("tests.logger")
    logger.handlers = []
    child_handler = mocker.Mock()
    child_handler.emit.side_effect = RuntimeError("boom")
    wrapper = DropOnFailHandler(child_handler)
    logger.addHandler(wrapper)

    wrapper.emit(log_record)
    wrapper.emit(log_record)

    assert wrapper._removed is True
    assert wrapper not in logger.handlers
    assert child_handler.emit.call_count == 2
