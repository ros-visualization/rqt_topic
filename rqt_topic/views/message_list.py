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

from python_qt_binding.QtCore import Slot
from python_qt_binding.QtWidgets import (
    QTableView
)

from packaging.version import Version  # noqa
from python_qt_binding import QT_BINDING_VERSION

if Version(QT_BINDING_VERSION) < Version('6.0.0'):
    SelectRows = QTableView.SelectRows
else:
    from python_qt_binding.QtWidgets import QAbstractItemView
    SelectRows = QAbstractItemView.SelectionBehavior.SelectRows


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

        self.setSelectionBehavior(SelectRows)

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
