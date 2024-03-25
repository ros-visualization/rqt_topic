import pytest

import rclpy

from rqt_topic.models.topic_list import (
    TopicListModel,
    TopicListProxy,
    generate_topic_list,
)

NUMBER_OF_TOPICS = 15

rclpy.init()


@pytest.fixture
def node():
    return rclpy.create_node('test_topic_list')


@pytest.fixture
def topic_list(node):
    return TopicListModel(topics=generate_topic_list(15))


@pytest.fixture
def topic_list_proxy(topic_list):
    return TopicListProxy(
        model=topic_list,
    )


def test_topic_list_model(
    topic_list,
    # qtmodeltester
):
    # qtmodeltester.check(topic_list)

    # Check model indexes
    first_row = topic_list.index(0, 0)
    assert first_row.row() == 0
    assert first_row.column() == 0
    assert first_row.data() == '/0/test_topic'

    middle_row = topic_list.index(7, 0)
    assert middle_row.row() == 7
    assert middle_row.column() == 0
    assert middle_row.data() == '/7/test_topic'

    last_row = topic_list.index(NUMBER_OF_TOPICS - 1, 0)
    assert last_row.row() == NUMBER_OF_TOPICS - 1
    assert last_row.column() == 0
    assert last_row.data() == f'/{NUMBER_OF_TOPICS - 1}/test_topic'

    last_row = topic_list.index(NUMBER_OF_TOPICS - 1, 2)
    assert last_row.row() == NUMBER_OF_TOPICS - 1
    assert last_row.column() == 2
    assert last_row.data() == '14.00 B/s'


def test_topic_list_proxy(
    topic_list_proxy,
    # qtmodeltester
):
    # qtmodeltester.check(topic_list_proxy)

    # Check model indexes
    first_row = topic_list_proxy.index(0, 0)
    assert first_row.row() == 0
    assert first_row.column() == 0
    assert first_row.data() == '/0/test_topic'

    middle_row = topic_list_proxy.index(7, 0)
    assert middle_row.row() == 7
    assert middle_row.column() == 0
    assert middle_row.data() == '/7/test_topic'

    last_row = topic_list_proxy.index(NUMBER_OF_TOPICS - 1, 0)
    assert last_row.row() == NUMBER_OF_TOPICS - 1
    assert last_row.column() == 0
    assert last_row.data() == f'/{NUMBER_OF_TOPICS - 1}/test_topic'

    last_row = topic_list_proxy.index(NUMBER_OF_TOPICS - 1, 2)
    assert last_row.row() == NUMBER_OF_TOPICS - 1
    assert last_row.column() == 2
    assert last_row.data() == '14.00 B/s'
