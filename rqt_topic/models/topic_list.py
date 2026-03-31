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

from typing import List

from packaging.version import Version
from python_qt_binding import QT_BINDING_VERSION

from python_qt_binding.QtCore import (
    QAbstractItemModel,
    QAbstractTableModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Slot,
)

if Version(QT_BINDING_VERSION) < Version('6.0.0'):
    BackgroundRole = Qt.BackgroundRole
    CheckStateRole = Qt.CheckStateRole
    DisplayRole = Qt.DisplayRole
    Checked = Qt.Checked
    Unchecked = Qt.Checked
    ItemIsSelectable = Qt.ItemIsSelectable
    ItemIsEnabled = Qt.ItemIsEnabled
    ItemIsUserCheckable = Qt.ItemIsUserCheckable
    Horizontal = Qt.Horizontal
    Vertical = Qt.Vertical
else:
    BackgroundRole = Qt.ItemDataRole.BackgroundRole
    CheckStateRole = Qt.ItemDataRole.CheckStateRole
    DisplayRole = Qt.ItemDataRole.DisplayRole
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Checked
    ItemIsSelectable = Qt.ItemFlag.ItemIsSelectable
    ItemIsEnabled = Qt.ItemFlag.ItemIsEnabled
    ItemIsUserCheckable = Qt.ItemFlag.ItemIsUserCheckable
    Horizontal = Qt.Orientation.Horizontal
    Vertical = Qt.Orientation.Vertical


from rqt_topic.models.topic import Bandwidth, Frequency, TopicModel
from rqt_topic.workers.topic import TopicWorker


class TopicListModel(QAbstractTableModel):
    def __init__(
        self, *args, window_id: int = 0, topics: List[TopicModel] = [], **kwargs
    ):
        super(TopicListModel, self).__init__(*args, **kwargs)
        self.window_id = window_id
        self.topics = topics
        # Remove all private attributes for user-facing columns
        self.columns = list(TopicModel.__fields__.keys())
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
        return any(topic.monitor for topic in self.topics)

    def monitoring_count(self):
        """Return the number of topics currently being monitored."""
        return len([True for topic in self.topics if topic.monitor])

    def data(self, index, role):
        """
        Call for every cell in the table, returns different things depending on the given role.

        TODO(evan.flynn): extend this to handle formatting / colors for specific
        data:

        https://www.pythonguis.com/tutorials/pyside-qtableview-modelviews-numpy-pandas/
        """
        assert self.checkIndex(index, QAbstractItemModel.CheckIndexOption.IndexIsValid)
        row, column_name = index.row(), self.columns[index.column()]
        topic = self.topics[row]
        data = getattr(topic, column_name, None)
        if role == DisplayRole:
            if column_name == 'bandwidth':
                return data.print_bps()
            elif column_name == 'frequency':
                return data.print_hz()
            elif column_name == 'timestamp':
                return data.isoformat() if data is not None else ''
            return str(data)
        # Use this role to set the background color of cells
        elif role == BackgroundRole:
            if not topic.message:
                return None
            return (
                topic.message.color_from_timestamp()
                if self.highlight_new_messages
                else None
            )

        # Checkbox in first column for monitoring the topic
        if role == CheckStateRole and index.column() == 0:
            return Checked if topic.monitor else Unchecked

    def setData(self, index, value, role):
        """Call whenever data is changed."""
        assert self.checkIndex(index, QAbstractItemModel.CheckIndexOption.IndexIsValid)
        # hack: is there a better way to get the current topic name?
        topic = self.topics[index.row()]
        if role == CheckStateRole:
            topic.monitor = value == Checked
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
            return ItemIsSelectable | ItemIsEnabled | ItemIsUserCheckable
        else:
            return ItemIsSelectable | ItemIsEnabled

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
        if role == DisplayRole:
            if orientation == Horizontal:
                return self.columns[index]
            elif orientation == Vertical:
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
