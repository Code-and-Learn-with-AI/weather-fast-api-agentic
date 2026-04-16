import json
import logging
from io import StringIO

from app.core.logging import setup_logging


def test_log_output_is_valid_json_with_required_fields() -> None:
    stream = StringIO()
    setup_logging(stream=stream)
    logging.getLogger("test").info("hello")
    record = json.loads(stream.getvalue().strip())
    assert "timestamp" in record
    assert "level" in record
    assert "message" in record
