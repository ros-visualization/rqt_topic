# Copyright 2025 Open Source Robotics Foundation, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the Willow Garage, Inc. nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from datetime import datetime
import re
from typing import List

from pydantic import BaseModel, ConfigDict, validator
from python_qt_binding.QtGui import QColor

TOPIC_RE = re.compile(r'^(\/([a-zA-Z0-9_]+))+$')


class MessageModel(BaseModel):
    timestamp: datetime = datetime.now()
    topic: str = ''
    message_type: str = ''
    content: dict = {}

    # TODO(evan.flynn): implement these later on
    # recorded_timestamp: Optional[str] = 'timestamp this message was recorded'
    # source_node: Optional[str] = 'node that sent this msg'

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        if not self.content:
            return ''
        return str(self.content)

    @validator('topic')
    def validate_topic(cls, value):
        assert TOPIC_RE.match(value) is not None, f'Given topic is not valid: {value}'
        return value

    @validator('timestamp')
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
        self.topic = ''
        self.message_type = ''
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
