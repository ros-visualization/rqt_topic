from python_qt_binding.QtCore import Slot
from python_qt_binding.QtWidgets import (
    QTableView,
)


class MessageListView(QTableView):
    def __init__(self, parent, model):
        super(MessageListView, self).__init__(parent=parent)

        self.model = model
        self.setSortingEnabled(True)
        self.setModel(model)

        self.horizontal_header = self.horizontalHeader()
        self.horizontal_header.setStretchLastSection(True)
        self.vertical_header = self.verticalHeader()
        self.vertical_header.setVisible(False)

        self.setSelectionBehavior(QTableView.SelectRows)

        self.scrollToBottom()

        # store this to use later
        self.scrollbar = self.verticalScrollBar()
        self.scrollbar.rangeChanged.connect(self.resize_scroll_area)

        self.model.dataChanged.connect(self.update_view_data)
        self.model.layoutChanged.connect(self.update_list)

    @Slot(int, int)
    def resize_scroll_area(self, min_scroll, max_scroll):
        self.scrollbar.setValue(max_scroll)

    @Slot()
    def update_view_data(self):
        # Scroll to the bottom automatically if scroll bar is already at the bottom
        if self.scrollbar.value() >= self.scrollbar.maximum():
            self.scrollToBottom()

    @Slot()
    def update_list(self):
        # TODO(evan.flynn): this slows down the GUI a lot if called every time
        # Investigate a smarter way to only call this when it's necessary
        # self.resizeColumnsToContents()

        # Scroll to the bottom automatically if scroll bar is already at the bottom
        if self.scrollbar.value() >= self.scrollbar.maximum():
            self.scrollToBottom()
