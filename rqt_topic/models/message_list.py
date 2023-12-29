import re

from python_qt_binding.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    Qt,
    QObject,
    QModelIndex,
    Signal,
    Slot,
)

from rqt_topic.models.message import MessageModel


class MessageListSignals(QObject):
    updateQueueSize = Signal(int)
    addMessage = Signal(MessageModel)


class MessageListModel(QAbstractTableModel):
    def __init__(self, *args, messages=None, **kwargs):
        super(MessageListModel, self).__init__(*args, **kwargs)
        self.messages = messages or []
        self.columns = list(MessageModel.model_fields.keys())
        self.highlight_new_messages = True

        self.signals = MessageListSignals()

        self.signals.updateQueueSize.connect(self.update_queue)
        self.signals.addMessage.connect(self.add_new_message)

    def data(self, index, role):
        """
        Called for every cell in the table, returns different things
        depending on the given role.
        """
        # TODO(evan.flynn): extend this to handle formatting / colors for specific
        # data:
        # https://www.pythonguis.com/tutorials/pyside-qtableview-modelviews-numpy-pandas/

        assert self.checkIndex(index)
        row, column = index.row(), self.columns[index.column()]
        msg = self.messages[row]
        if role == Qt.DisplayRole:
            value = getattr(msg, column, None)
            if not value or not msg.topic or not msg.message_type:
                return ""
            if column == 'timestamp':
                return msg.timestamp.isoformat()
            return str(value)
        # Use this role to set the background color of cells
        elif role == Qt.BackgroundRole:
            return msg.color_from_timestamp() if self.highlight_new_messages else None

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.columns)

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return 0
        return len(self.messages)

    def headerData(self, index, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.columns[index]
            elif orientation == Qt.Vertical:
                return index + 1  # starts at 0, so +1
        return None

    @Slot(int)
    def update_queue(self, queue_size: int = 100):
        """Fill the message list with dummy data up to the new input queue limit."""
        # Update queue size with new value
        self.queue_size = queue_size
        # In case queue size was decreased
        while len(self.messages) > self.queue_size:
            self.messages.pop(0)
        while len(self.messages) < self.queue_size:
            self.messages.append(MessageModel())
        # rows were added, so emit a layoutChanged signal
        self.layoutChanged.emit()

    def update_row(self, row: int):
        if row == -1:
            row = len(self.messages) - 1
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, len(self.columns) - 1)
        )

    @Slot(MessageModel)
    def add_new_message(self, msg: MessageModel):
        # Add msg to end of list
        self.messages.append(msg)
        if len(self.messages) > self.queue_size:
            self.messages.pop(0)
        # Update the last row
        self.update_row(-1)

    def clear(self):
        for row, msg in enumerate(self.messages):
            msg.clear()
            self.update_row(row)


class MessageListProxySignals(QObject):
    searchForStr = Signal(str)


class MessageListProxy(QSortFilterProxyModel):
    """A proxy model to enable sort and filtering of the underlying MessageListModel."""

    def __init__(self, model: MessageListModel, parent=None):
        super(MessageListProxy, self).__init__(parent)
        self.model = model
        self.setSourceModel(self.model)

        self.signals = MessageListProxySignals()

        self.signals.searchForStr.connect(self.update_search_filter)

        self.query_string = ""
        self.queryRE = re.compile(r'.*')

    @Slot(str)
    def update_search_filter(self, search_query: str):
        self.query_string = search_query
        # for now use the same regex for all columns, could be enhanced down the road
        self.queryRE = re.compile(search_query)
        self.invalidateFilter()

    def matches_query(self, value: str) -> bool:
        return self.queryRE.match(value) is not None or self.query_string in value

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        """Return true if row should be displayed, false otherwise."""
        model = self.sourceModel()
        message = model.messages[sourceRow]

        # Don't display the row if the topic or message type are not known
        if not message.topic or not message.message_type:
            return False

        if self.query_string or self.queryRE:
            if any(
                [
                    self.matches_query(
                        str(model.index(sourceRow, column, sourceParent).data())
                    )
                    for column in range(len(model.columns))
                ]
            ):
                return True
        return False
