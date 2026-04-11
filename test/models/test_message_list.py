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

import pytest

from rqt_topic.models.message import generate_test_msgs
from rqt_topic.models.message_list import (
    DisplayRole,
    MessageListModel,
    MessageListProxy,
)


@pytest.fixture
def message_list():
    return MessageListModel(
        messages=generate_test_msgs(10),
    )


@pytest.fixture
def message_list_proxy(message_list):
    return MessageListProxy(
        model=message_list,
    )


def test_message_list_model(
    message_list,
    # qtmodeltester
):
    # qtmodeltester.check(message_list)

    timestamp_str = message_list.data(message_list.index(0, 0), role=DisplayRole)
    # Ensure timestamp follows ISO format
    assert datetime.fromisoformat(timestamp_str)
    assert (
        message_list.data(
            message_list.index(0, 1),
            role=DisplayRole,
        )
        == '/0/test_topic'
    )
    assert (
        message_list.data(
            message_list.index(0, 2),
            role=DisplayRole,
        )
        == 'test_msgs/BasicTypes'
    )
    assert (
        message_list.data(
            message_list.index(0, 3),
            role=DisplayRole,
        )
        == "{'test_0_key': 'value_0'}"
    )

    # Check last topic is also there
    assert (
        message_list.data(
            message_list.index(9, 1),
            role=DisplayRole,
        )
        == '/9/test_topic'
    )


def test_message_list_proxy(
    message_list_proxy,
    # qtmodeltester
):
    # qtmodeltester.check(message_list_proxy)

    timestamp_str = message_list_proxy.data(
        message_list_proxy.index(0, 0), role=DisplayRole
    )
    # Ensure timestamp follows ISO format
    assert datetime.fromisoformat(timestamp_str)
    assert (
        message_list_proxy.data(
            message_list_proxy.index(0, 1),
            role=DisplayRole,
        )
        == '/0/test_topic'
    )
    assert (
        message_list_proxy.data(
            message_list_proxy.index(0, 2),
            role=DisplayRole,
        )
        == 'test_msgs/BasicTypes'
    )
    assert (
        message_list_proxy.data(
            message_list_proxy.index(0, 3),
            role=DisplayRole,
        )
        == "{'test_0_key': 'value_0'}"
    )

    # Check last topic is also there
    assert (
        message_list_proxy.data(
            message_list_proxy.index(9, 1),
            role=DisplayRole,
        )
        == '/9/test_topic'
    )
