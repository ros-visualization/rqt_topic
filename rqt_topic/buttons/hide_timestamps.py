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

from packaging.version import Version
from python_qt_binding import QT_BINDING_VERSION
if Version(QT_BINDING_VERSION) < Version('6.0.0'):
    from python_qt_binding.QtWidgets import QAction
else:
    from python_qt_binding.QtGui import QAction


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
