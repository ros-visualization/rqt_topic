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

from python_qt_binding.QtCore import Qt

from rqt_topic.models.message_detail import MessageDetailModel, MessageDetailProxy


TEST_MSG_DICT = {
    'header': {
        'frame_id': 'test',
        'timestamp': {
            'sec': 100,
            'nsec': 5,
        },
    },
    'content': 'test_content',
}


@pytest.fixture
def message_detail():
    return MessageDetailModel(
        message=TEST_MSG_DICT,
    )


@pytest.fixture
def message_detail_proxy(message_detail):
    return MessageDetailProxy(
        model=message_detail,
    )


def test_basic_message_detail_model():
    field_item = MessageDetailModel()

    assert len(field_item.children) == 0

    field_item.parse_msg_dict(TEST_MSG_DICT)

    assert len(field_item.children) == 2
    assert field_item.message == TEST_MSG_DICT

    assert field_item.name == 'message'
    assert field_item.children[0].name == 'header'
    assert field_item.children[0].children[0].name == 'frame_id'
    assert field_item.children[0].children[0].message == 'test'
    assert field_item.children[0].children[1].name == 'timestamp'
    assert field_item.children[0].children[1].children[0].name == 'sec'
    assert field_item.children[0].children[1].children[0].message == 100
    assert field_item.children[0].children[1].children[1].name == 'nsec'
    assert field_item.children[0].children[1].children[1].message == 5
    assert field_item.children[1].name == 'content'

    # Check model indexes
    header_index = field_item.index(0, 0)
    assert header_index.row() == 0
    assert header_index.column() == 0
    assert header_index.data() == 'header'

    timestamp_index = field_item.index(1, 0, header_index)
    assert timestamp_index.row() == 1
    assert timestamp_index.column() == 0
    assert timestamp_index.data() == 'timestamp'

    # Test a different way to get an index
    nsec_index = timestamp_index.internalPointer().index(1, 1)
    assert nsec_index.row() == 1
    assert nsec_index.column() == 1
    assert nsec_index.data() == '5'


def test_message_detail_model(
    message_detail,
    # qtmodeltester
):
    # qtmodeltester.check(message_detail)

    assert (
        message_detail.data(message_detail.index(0, 0), role=Qt.DisplayRole) == 'header'
    )
    assert (
        message_detail.data(message_detail.index(0, 1), role=Qt.DisplayRole)
        == "{'frame_id': 'test', 'timestamp': {'sec': 100, 'nsec': 5}}"
    )
    assert (
        message_detail.data(message_detail.index(1, 0), role=Qt.DisplayRole)
        == 'content'
    )
    assert (
        message_detail.data(message_detail.index(1, 1), role=Qt.DisplayRole)
        == 'test_content'
    )


def test_message_detail_proxy_model(
    message_detail_proxy,
    # qtmodeltester,
):
    message_detail_proxy.sourceModel().update(TEST_MSG_DICT)
    # qtmodeltester.check(message_detail_proxy)

    # Check model indexes
    header_index = message_detail_proxy.index(0, 0)
    assert header_index.row() == 0
    assert header_index.column() == 0
    assert header_index.data() == 'header'

    timestamp_index = message_detail_proxy.index(1, 0, header_index)
    assert timestamp_index.row() == 1
    assert timestamp_index.column() == 0
    assert timestamp_index.data() == 'timestamp'

    nsec_index = message_detail_proxy.index(1, 1, timestamp_index)
    assert nsec_index.row() == 1
    assert nsec_index.column() == 1
    assert nsec_index.data() == '5'

    # Update search filter to filter only for rows that contain `f`
    message_detail_proxy.update_search_filter('f')

    # Check model indexes
    # show the frame_id row and its parents
    header_index = message_detail_proxy.index(0, 0)
    assert header_index.row() == 0
    assert header_index.column() == 0
    assert header_index.data() == 'header'

    # show the frame_id row and its parents
    frameid_index = message_detail_proxy.index(0, 0, header_index)
    assert frameid_index.row() == 0
    assert frameid_index.column() == 0
    assert frameid_index.data() == 'frame_id'

    # show the frame_id row and its parents
    frameid_index = message_detail_proxy.index(0, 1, header_index)
    assert frameid_index.row() == 0
    assert frameid_index.column() == 1
    assert frameid_index.data() == 'test'

    # The timestamp row should be hidden now though
    timestamp_index = message_detail_proxy.index(1, 0, header_index)
    assert timestamp_index.row() == -1
    assert timestamp_index.column() == -1
