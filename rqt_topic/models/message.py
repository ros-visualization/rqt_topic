from datetime import datetime
from typing import List

from python_qt_binding.QtGui import QColor
from pydantic import BaseModel, ConfigDict, field_validator
import re

TOPIC_RE = re.compile(r'^(\/([a-zA-Z0-9_]+))+$')


class MessageModel(BaseModel):
    timestamp: datetime = datetime.now()
    topic: str = ""
    message_type: str = ""
    content: dict = {}

    # TODO(evan.flynn): implement these later on
    # recorded_timestamp: Optional[str] = 'timestamp this message was recorded'
    # source_node: Optional[str] = 'node that sent this msg'

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        if not self.content:
            return ""
        return str(self.content)

    @field_validator('topic')
    def validate_topic(cls, value):
        assert TOPIC_RE.match(value) is not None, f'Given topic is not valid: {value}'
        return value

    @field_validator('timestamp')
    def validate_timestamp(cls, value):
        return value

    def total_seconds_old(self) -> datetime:
        return (datetime.now() - self.timestamp).total_seconds()

    def color_from_timestamp(self) -> QColor:
        # multiply by 30 to scale / excentuate the alpha value, clip between 0 and 150
        alpha = max(0, min(150, 150 - int(self.total_seconds_old() * 30)))
        return QColor(90, 90, 90, alpha)

    def clear(self):
        self.timestamp = datetime.now()
        self.topic = ""
        self.message_type = ""
        self.content = {}


def generate_test_msgs(number_of_msgs: int = 100) -> List[MessageModel]:
    """Generate a list of messages for testing."""
    return [
        MessageModel(
            topic=f'/{i}/test_topic',
            message_type='test_msgs/BasicTypes',
            timestamp=datetime.now(),
            content={f'test_{i}_key': f'value_{i}'},
        )
        for i in range(number_of_msgs)
    ]
