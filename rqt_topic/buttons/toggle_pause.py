from python_qt_binding.QtWidgets import QAction, QStyle


class TogglePause(QAction):
    def __init__(self, style, name: str = 'Pause'):
        super(TogglePause, self).__init__(name)

        # Style is provided by the widget that uses this button
        self.style = style

        self.pause_icon = self.style.standardIcon(QStyle.SP_MediaPause)
        self.play_icon = self.style.standardIcon(QStyle.SP_MediaPlay)

        self.setIcon(self.pause_icon)
        self.setIconText('Pause')
        self.setStatusTip('Pause the view')
        self._paused = False

        self.triggered.connect(self.toggle_pause)

    def is_paused(self) -> bool:
        return self._paused

    def toggle_pause(self):
        if self._paused:
            self.resume()
        else:
            self.pause()

    def pause(self):
        """Button is paused."""
        self.setIcon(self.play_icon)
        self.setText('Resume')
        self.setStatusTip('Resume the view')
        self._paused = True

    def resume(self):
        """Button is resumed."""
        self.setIcon(self.pause_icon)
        self.setText('Pause')
        self.setStatusTip('Pause the view')
        self._paused = False
