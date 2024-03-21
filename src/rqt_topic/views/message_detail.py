from python_qt_binding.QtCore import Slot
from python_qt_binding.QtWidgets import QTreeView


class MessageDetailView(QTreeView):
    def __init__(self, parent, model):
        super(MessageDetailView, self).__init__(parent=parent)

        self.model = model
        self.setModel(model)

        self.model.layoutChanged.connect(self.update_view)
        self.model.dataChanged.connect(self.update_data_view)

        self.expandAll()

    @Slot()
    def update_view(self):
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)

    @Slot()
    def update_data_view(self):
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
