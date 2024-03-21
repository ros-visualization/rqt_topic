from python_qt_binding.QtWidgets import QAction


class ResizeColumns(QAction):
    def __init__(self, style, name: str = "Resize columns to contents"):
        super(ResizeColumns, self).__init__(name)

        # Style is provided by the widget that uses this button
        self.style = style

        self.setStatusTip("Resize columns to contents")
