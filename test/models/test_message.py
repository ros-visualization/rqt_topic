import pytest
from datetime import datetime

from pydantic import ValidationError

from rqt_topic.models.message import generate_test_msgs, MessageModel


def test_message_model_happy_path():
    test_msgs = generate_test_msgs(10)

    for index, msg in enumerate(test_msgs):
        assert msg.topic == f'/{index}/test_topic'
        assert msg.message_type == 'test_msgs/BasicTypes'
        assert isinstance(msg.timestamp, datetime)
        assert msg.content == {f'test_{index}_key': f'value_{index}'}


def test_message_model_incomplete_inputs():
    test_msg = None
    with pytest.raises(ValidationError) as error:
        test_msg = MessageModel(
            topic='/invalid@$_topic@$@^', message_type='test_msgs/BasicTypes'
        )
    assert 'Given topic is not valid: /invalid@$_topic@$@^' in str(error.value)

    with pytest.raises(ValidationError) as error:
        test_msg = MessageModel(
            topic='/test_topic',
            message_type='test_msgs/BasicTypes',
            timestamp='invalid timestamp',
        )
    assert 'invalid datetime format' in str(error.value)
    assert test_msg is None
