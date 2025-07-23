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
from typing import List

from pydantic import BaseModel
from typing import Optional

from rqt_topic.models.message import MessageModel


# TODO(evan.flynn): these could probably be moved to ros2topic
class Bandwidth(BaseModel):
    bytes_per_sec: float = 0.0
    samples: int = 0
    mean: float = 0.0
    min_size: float = 0.0
    max_size: float = 0.0

    def clear(self):
        self.bytes_per_sec = 0.0
        self.samples = 0.0
        self.mean = 0.0
        self.min_size = 0.0
        self.max_size = 0.0

    def fill(self, bytes_per_sec, samples, mean, min_size, max_size):
        self.bytes_per_sec = bytes_per_sec
        self.samples = samples
        self.mean = mean
        self.min_size = min_size
        self.max_size = max_size

    def print_bps(self) -> str:
        bw_str = ""
        if self.bytes_per_sec is None:
            bw_str = 'unknown'
        elif self.bytes_per_sec < 1000:
            bw_str = '%.2f B/s' % self.bytes_per_sec
        elif self.bytes_per_sec < 1000000:
            bw_str = '%.2f KB/s' % (self.bytes_per_sec / 1000.0)
        else:
            bw_str = '%.2f MB/s' % (self.bytes_per_sec / 1000000.0)
        return bw_str


# TODO(evan.flynn): these could probably be moved to ros2topic
class Frequency(BaseModel):
    rate: float = 0.0
    min_delta: float = 0.0
    max_delta: float = 0.0
    std_dev: float = 0.0
    samples: int = 0

    def clear(self):
        self.rate = 0.0
        self.min_delta = 0.0
        self.max_delta = 0.0
        self.std_dev = 0.0
        self.samples = 0.0

    def fill(self, rate, min_delta, max_delta, std_dev, samples):
        self.rate = rate * 1e9
        self.min_delta = min_delta
        self.max_delta = max_delta
        self.std_dev = std_dev
        self.samples = samples

    def print_hz(self):
        return '%1.2f Hz' % self.rate if self.rate is not None else 'unknown'


class TopicModel(BaseModel):
    name: str = ""
    message_type: str = ""
    bandwidth: Bandwidth = Bandwidth()
    frequency: Frequency = Frequency()
    monitor: bool = False

    timestamp: datetime = datetime.now()
    message: MessageModel = MessageModel()

    # A topic can have multiple nodes publishing to the same topic
    source_nodes: Optional[List[str]] = ['node1', 'node2', 'node3']

    def clear(self):
        self.bandwidth.clear()
        self.frequency.clear()
        self.message.clear()
        self.source_nodes.clear()


def generate_test_topics(number_of_topics: int = 10) -> List[TopicModel]:
    """Generate a list of topics for testing."""
    return [
        TopicModel(
            name=f'/{i}/test_topic',
            message_type='test_msgs/BasicTypes',
            bandwidth=Bandwidth(bytes_per_sec=float(i)),
            frequency=Frequency(rate=float(i)),
        )
        for i in range(number_of_topics)
    ]
