from typing import List

from python_qt_binding.QtCore import (
    QAbstractItemModel,
    QAbstractTableModel,
    QSortFilterProxyModel,
    Qt,
    Slot,
    QModelIndex,
)

from rqt_topic.models.topic import TopicModel, Bandwidth, Frequency
from rqt_topic.workers.topic import TopicWorker


class TopicListModel(QAbstractTableModel):
    def __init__(
        self, *args, window_id: int = 0, topics: List[TopicModel] = [], **kwargs
    ):
        super(TopicListModel, self).__init__(*args, **kwargs)
        self.window_id = window_id
        self.topics = topics
        # Remove all private attributes for user-facing columns
        self.columns = list(TopicModel.model_fields.keys())
        self.row_colors = {}
        # Monitor is not a column but a checkbox in column 1
        self.columns.remove('monitor')
        # Remove source nodes for now until it is implemented
        self.columns.remove('source_nodes')

        self.highlight_new_messages = True

        # Dictionary of workers where key is topic name, value is the TopicWorker
        self.workers = {}

    def monitoring(self):
        """Return True if any topics are currently being monitored."""
        return any([topic.monitor for topic in self.topics])

    def monitoring_count(self):
        """Return the number of topics currently being monitored."""
        return len([True for topic in self.topics if topic.monitor])

    def data(self, index, role):
        """
        Called for every cell in the table, returns different things
        depending on the given role.

        TODO(evan.flynn): extend this to handle formatting / colors for specific
        data:

        https://www.pythonguis.com/tutorials/pyside-qtableview-modelviews-numpy-pandas/
        """
        assert self.checkIndex(index, QAbstractItemModel.CheckIndexOption.IndexIsValid)
        row, column_name = index.row(), self.columns[index.column()]
        topic = self.topics[row]
        data = getattr(topic, column_name, None)
        if role == Qt.DisplayRole:
            if column_name == 'bandwidth':
                return data.print_bps()
            elif column_name == 'frequency':
                return data.print_hz()
            elif column_name == 'timestamp':
                return data.isoformat() if data is not None else ""
            return str(data)
        # Use this role to set the background color of cells
        elif role == Qt.BackgroundRole:
            if not topic.message:
                return None
            return (
                topic.message.color_from_timestamp()
                if self.highlight_new_messages
                else None
            )

        # Checkbox in first column for monitoring the topic
        if role == Qt.CheckStateRole and index.column() == 0:
            return Qt.Checked if topic.monitor else Qt.Unchecked

    def setData(self, index, value, role):
        """Called whenever data is changed."""
        assert self.checkIndex(index, QAbstractItemModel.CheckIndexOption.IndexIsValid)
        # hack: is there a better way to get the current topic name?
        topic = self.topics[index.row()]
        if role == Qt.CheckStateRole:
            topic.monitor = value == Qt.Checked
            if topic.monitor:
                self.create_topic_worker(topic)
            else:
                self.delete_topic_worker(topic)
        self.dataChanged.emit(index, index)
        return True

    def delete_topic_worker(self, topic: TopicModel):
        topic_worker = (
            self.workers.pop(topic.name) if topic.name in self.workers else None
        )
        if topic_worker:
            topic_worker.stop()
            topic_worker.signals.update_topic.disconnect()
            del topic_worker

    def create_topic_worker(self, topic: TopicModel):
        if topic.name not in self.workers:
            # Create worker for the current topic
            self.workers[topic.name] = TopicWorker(
                window_id=self.window_id, topic=topic
            )
        self.workers[topic.name].signals.update_topic.connect(self.update_topic)
        # Start worker for the current topic
        self.workers[topic.name].run()  # (topic)

    def flags(self, index):
        if not index.isValid():
            return None
        assert self.checkIndex(index, QAbstractItemModel.CheckIndexOption.IndexIsValid)
        if index.column() == 0:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        if parent.isValid():
            assert self.checkIndex(
                parent, QAbstractItemModel.CheckIndexOption.IndexIsValid
            )
            return 0
        return len(self.columns)

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            assert self.checkIndex(
                parent, QAbstractItemModel.CheckIndexOption.IndexIsValid
            )
            return 0
        return len(self.topics)

    def available_topics(self):
        """Return list of all topic names currently in model."""
        # TODO(evan.flynn): topics might have multiple different message types?
        return [(topic.name, [topic.message_type]) for topic in self.topics]

    def headerData(self, index: int, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[index]
            elif orientation == Qt.Vertical:
                return index + 1  # starts at 0, so +1
        return None

    def update_row(self, row: int):
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, len(self.columns) - 1)
        )

    @Slot(TopicModel)
    def update_topic(self, topic: TopicModel):
        """Update a topic with the given TopicModel."""
        topic_names = [t.name for t in self.topics]
        if topic.name in topic_names:
            # topic already exists, just update the data
            row = topic_names.index(topic.name)
            self.topics[row] = topic
            self.update_row(row + 1)
        else:
            # topic is new, append to the list and emit that the layout has changed
            self.topics.append(topic)
            self.layoutChanged.emit()

    @Slot(TopicModel)
    def stop_monitoring(self, topic: TopicModel):
        """Stop monitoring a topic."""
        if topic in self.topics:
            row = self.topics.index(topic)
            self.topics[row].monitor = False
            self.update_row(row)

    @Slot(TopicModel)
    def clear_topic(self, topic: TopicModel):
        if topic in self.topics:
            row = self.topics.index(topic)
            self.topics[row].clear()
            self.update_row(row)

    def clear(self):
        [self.clear_topic(topic) for topic in self.topics]


def generate_topic_list(number_of_topics: int = 10):
    return [
        TopicModel(
            name=f'/{i}/test_topic',
            message_type='test_msgs/BasicTypes',
            bandwidth=Bandwidth(bytes_per_sec=float(i)),
            frequency=Frequency(rate=float(i)),
        )
        for i in range(number_of_topics)
    ]


class TopicListProxy(QSortFilterProxyModel):
    """A proxy model to enable sort and filtering of the underlying TopicListModel."""

    def __init__(self, model: TopicListModel, parent=None):
        super(TopicListProxy, self).__init__(parent)
        self.setSourceModel(model)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex):
        """Return true if row should be displayed, false otherwise."""
        return True
