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


def test_message_detail_model(message_detail, qtmodeltester):
    # qtmodeltester.check(message_detail)

    assert (
        message_detail.data(message_detail.index(0, 0), role=Qt.DisplayRole) == 'header'
    )
    assert (
        message_detail.data(message_detail.index(0, 1), role=Qt.DisplayRole)
        == '{\'frame_id\': \'test\', \'timestamp\': {\'sec\': 100, \'nsec\': 5}}'
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
    qtmodeltester,
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
