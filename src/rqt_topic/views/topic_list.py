from python_qt_binding.QtCore import Slot
from python_qt_binding.QtWidgets import (
    QTableView,
)


class TopicListView(QTableView):
    def __init__(self, parent, model):
        super(TopicListView, self).__init__(parent=parent)

        self.model = model
        self.setSortingEnabled(True)
        self.setModel(model)

        self.horizontal_header = self.horizontalHeader()
        self.vertical_header = self.verticalHeader()
        self.horizontal_header.setStretchLastSection(True)

        self.setSelectionBehavior(QTableView.SelectRows)
        self.resizeColumnsToContents()

        self.model.dataChanged.connect(self.update_view_data)
        self.model.layoutChanged.connect(self.update_view)

    def topic_is_selected(self, topic: str) -> bool:
        """Check if the given topic is currently selected."""
        indexes = self.selectedIndexes()
        result = False
        if indexes:
            result = any(
                [True for index in indexes if index.isValid() if index.data() == topic]
            )
        return result

    @Slot()
    def update_view(self):
        self.resizeColumnsToContents()

    @Slot()
    def update_view_data(self):
        pass
