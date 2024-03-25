from python_qt_binding.QtWidgets import QAction


class ToggleHighlight(QAction):
    def __init__(self, style, name: str = 'Disable highlighting'):
        super(ToggleHighlight, self).__init__(name)

        # Style is provided by the widget that uses this button
        self.style = style

        self.setStatusTip('Disable color highlighting for new messages')
        self.triggered.connect(self.toggle_highlight)
        self._is_highlighting = True

    def is_highlighting(self) -> bool:
        return self._is_highlighting

    def toggle_highlight(self):
        if self._is_highlighting:
            self.no_highlight()
        else:
            self.highlight()

    def highlight(self):
        """Turn color highlighting on."""
        self.setText('Disable highlighting')
        self.setStatusTip('Disable color highlighting for new messages')
        self._is_highlighting = True

    def no_highlight(self):
        """Turn color highlighting off."""
        self.setText('Highlight new messages')
        self.setStatusTip('Do not highlight rows for new messages')
        self._is_highlighting = False
