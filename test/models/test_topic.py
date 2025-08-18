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

import pytest

from rqt_topic.models.topic import (
    Bandwidth,
    Frequency,
    generate_test_topics,
)

NUMBER_OF_TOPICS = 15


@pytest.fixture
def topics():
    return generate_test_topics(NUMBER_OF_TOPICS)


def test_bandwidth():
    bw = Bandwidth()
    bw.fill(
        bytes_per_sec=25.0,
        samples=10,
        mean=30.0,
        min_size=1.0,
        max_size=50.0,
    )

    assert bw.bytes_per_sec == 25.0
    assert bw.samples == 10
    assert bw.mean == 30.0
    assert bw.min_size == 1.0
    assert bw.max_size == 50.0

    bw.clear()

    assert bw.bytes_per_sec == 0.0


def test_frequency():
    fq = Frequency()
    fq.fill(
        rate=0.00000001,
        min_delta=8.6,
        max_delta=7.5,
        std_dev=3.0,
        samples=9,
    )

    assert fq.rate == 10.0
    assert fq.min_delta == 8.6
    assert fq.max_delta == 7.5
    assert fq.std_dev == 3.0
    assert fq.samples == 9


def test_topic_model(topics):
    assert len(topics) == NUMBER_OF_TOPICS
    for i, topic in enumerate(topics):
        assert topic.name == f'/{i}/test_topic'
        assert topic.message_type == 'test_msgs/BasicTypes'
        assert topic.bandwidth.bytes_per_sec == float(i)
        assert topic.frequency.rate == float(i)
