import pytest
from datetime import datetime

from python_qt_binding.QtCore import Qt

from rqt_topic.models.message_list import MessageListModel, MessageListProxy
from rqt_topic.models.message import generate_test_msgs


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

    timestamp_str = message_list.data(message_list.index(0, 0), role=Qt.DisplayRole)
    # Ensure timestamp follows ISO format
    assert datetime.fromisoformat(timestamp_str)
    assert (
        message_list.data(
            message_list.index(0, 1),
            role=Qt.DisplayRole,
        )
        == '/0/test_topic'
    )
    assert (
        message_list.data(
            message_list.index(0, 2),
            role=Qt.DisplayRole,
        )
        == 'test_msgs/BasicTypes'
    )
    assert (
        message_list.data(
            message_list.index(0, 3),
            role=Qt.DisplayRole,
        )
        == '{\'test_0_key\': \'value_0\'}'
    )

    # Check last topic is also there
    assert (
        message_list.data(
            message_list.index(9, 1),
            role=Qt.DisplayRole,
        )
        == '/9/test_topic'
    )


def test_message_list_proxy(
    message_list_proxy,
    # qtmodeltester
):
    # qtmodeltester.check(message_list_proxy)

    timestamp_str = message_list_proxy.data(
        message_list_proxy.index(0, 0), role=Qt.DisplayRole
    )
    # Ensure timestamp follows ISO format
    assert datetime.fromisoformat(timestamp_str)
    assert (
        message_list_proxy.data(
            message_list_proxy.index(0, 1),
            role=Qt.DisplayRole,
        )
        == '/0/test_topic'
    )
    assert (
        message_list_proxy.data(
            message_list_proxy.index(0, 2),
            role=Qt.DisplayRole,
        )
        == 'test_msgs/BasicTypes'
    )
    assert (
        message_list_proxy.data(
            message_list_proxy.index(0, 3),
            role=Qt.DisplayRole,
        )
        == '{\'test_0_key\': \'value_0\'}'
    )

    # Check last topic is also there
    assert (
        message_list_proxy.data(
            message_list_proxy.index(9, 1),
            role=Qt.DisplayRole,
        )
        == '/9/test_topic'
    )
