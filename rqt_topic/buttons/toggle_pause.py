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
