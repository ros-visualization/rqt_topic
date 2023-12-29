from python_qt_binding.QtWidgets import QAction


# TODO(evan.flynn): it'd be better to make a generic "hideColumn" feature directly
# in the QAbstractTableModel. This is an acceptable work around for now.
class HideTimestamps(QAction):
    def __init__(self, style, name: str = 'Hide timestamps'):
        super(HideTimestamps, self).__init__(name)

        # Style is provided by the widget that uses this button
        self.style = style

        self.setStatusTip('Hide the timestamp columns from all views')
        self.triggered.connect(self.toggle_hide)
        self._hidden = False

    def is_hidden(self) -> bool:
        return self._hidden

    def toggle_hide(self):
        if self._hidden:
            self.unhide()
        else:
            self.hide()

    def hide(self):
        """Timestamps are hidden."""
        self.setText('Unhide timestamps')
        self.setStatusTip('Unhide the timestamp columns from all views')
        self._hidden = True

    def unhide(self):
        """Button is resumed."""
        self.setText('Hide timestamps')
        self.setStatusTip('Hide the timestamp columns from all views')
        self._hidden = False
