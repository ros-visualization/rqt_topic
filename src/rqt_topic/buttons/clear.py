from python_qt_binding.QtWidgets import QAction, QStyle


class Clear(QAction):
    def __init__(self, style, name: str = "Clear All"):
        super(Clear, self).__init__(name)

        # Style is provided by the widget that uses this button
        self.style = style

        self.clear_icon = self.style.standardIcon(QStyle.SP_DialogResetButton)

        self.setIcon(self.clear_icon)
        self.setIconText("Clear All")
        self.setStatusTip("Clear all the views")
