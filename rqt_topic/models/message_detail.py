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

from __future__ import annotations

import re
from typing import Any, List, Union

from python_qt_binding.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QObject,
    QSortFilterProxyModel,
    Qt,
    Signal,
    Slot,
)


class MessageDetailSignals(QObject):
    updateMsg = Signal(object)


class MessageDetailModel(QAbstractItemModel):
    def __init__(
        self,
        name: str = 'message',
        message: Any = {},
        parent_model: 'MessageDetailModel' = None,
        *args,
        **kwargs,
    ):
        super(MessageDetailModel, self).__init__(*args, **kwargs)
        self.name = name
        self.message = message
        self.parent_model = parent_model
        self.children: List[MessageDetailModel] = []

        self.signals = MessageDetailSignals()
        self.signals.updateMsg.connect(self.update)
        self.signals.updateMsg.emit(self.message)

        # Today just Field and content but down the road possibly split
        # each content into different columns? (e.g. vector split into three columns)
        self.columns = ['Field', 'Content']

    def create_new_msg(self, msg: dict):
        assert isinstance(msg, dict)
        self.parse_msg_dict(msg=msg, parent_model=self)

    @Slot(object)
    def update(self, msg: Any):
        if self.is_new_message_type(msg):
            self.clear()

        num_children = len(self.children)
        if isinstance(msg, dict):
            self.parse_msg_dict(msg)
        else:
            self.message = msg

        if num_children != len(self.children):
            self.layoutChanged.emit()

    def is_new_message_type(self, msg) -> bool:
        if isinstance(msg, dict):
            return self.message.keys() != msg.keys()
        else:
            return not isinstance(self.message, type(msg))

    def clear(self):
        self.message = {}
        self.children = []
        self.layoutChanged.emit()

    def reset(self):
        self.message = {}

    def row(self) -> int:
        if self.parent_model is None or not self.parent_model.children:
            return -1

        row = 0
        for i, child in enumerate(self.parent_model.children):
            if child == self:
                row = i
        return row

    def get_child(self, field: str) -> Union['MessageDetailModel', None]:
        if not str(field):
            # Field is blank, dont bother looking for children
            return None

        children = [child for child in self.children if str(child.name) == str(field)]
        if not children:
            # No children found matching given field
            return None

        assert len(children) == 1, (
            f'Multiple children below {self.name} with the same field name:\n'
            + '\tfield: {field}\n\tchildren:\n'
            + ''.join([f'\t\t{child.name}: {child.message}\n' for child in children])
        )
        return children[0]

    def index(self, row, column, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self
        if row < 0 or row >= node.rowCount():
            return QModelIndex()
        return self.createIndex(row, column, node.children[row])

    def parent(self, child: QModelIndex = QModelIndex()) -> QModelIndex:
        if child.isValid():
            node = child.internalPointer()
        else:
            node = self
        parent = node.parent_model
        if parent is None or parent.parent_model is None:
            return QModelIndex()
        return parent.index(parent.row(), 0)

    def data(self, index: QModelIndex, role: int = None):
        if index.isValid() and role == Qt.DisplayRole:
            node = index.internalPointer()
            if index.column() == 0:
                return str(node.name)
            elif index.column() == 1:
                return str(node.message)
            else:
                return None
        return None

    def setData(self, index, value: 'MessageDetailModel', role=Qt.EditRole):
        if index.isValid():
            if index.column() == 0:
                assert index.row() < len(self.children)
                child = self.get_child(value.name)
                if value.name == self.name:
                    self.message = value.message
                elif value.name == child.name:
                    child.message = value.message
                self.dataChanged.emit(index, index)
                return True
        return False

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() and parent.column() != 0:
            return 0
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self
        return len(node.children)

    def headerData(self, section, orientation, role) -> str:
        if role == Qt.DisplayRole:
            if section == 0:
                return 'Field'
            elif section == 1:
                return 'Data'

    def hasChildren(self, parent: QModelIndex = QModelIndex()) -> bool:
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self
        if node.rowCount() > 0:
            return True
        return False

    def buddy(self, index: QModelIndex) -> QModelIndex:
        return index

    def canFetchMore(self, parent: QModelIndex) -> bool:
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self
        return self.row() < node.rowCount()

    def fetchMore(self, parent: QModelIndex):
        if parent.isValid():
            return
        start = self.row()
        remainder = self.rowCount() - start
        if remainder <= 0:
            return
        # self.beginInsertRows(QModelIndex(), start, start + remainder - 1)
        # self.endInsertRows()
        return

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return None
        # assert self.checkIndex(index, QAbstractItemModel.CheckIndexOption.IndexIsValid)
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def span(self, index: QModelIndex):
        pass

    def hasIndex(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> bool:
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self
        if row < 0 or column < 0:
            return False
        if row < (node.rowCount() - 1) and column < (node.columnCount() - 1):
            return True
        return False

    def parse_msg_dict(
        self,
        msg: dict,
        parent_model: 'MessageDetailModel' = None,
    ) -> 'MessageDetailModel':
        """Recursively parse a given message dictionary."""
        if parent_model is None:
            parent_model = self

        parent_model.message = msg

        row = 0
        for field, value in msg.items():
            current_field = parent_model.get_child(field)
            if current_field is not None:
                # Current field already exists, just update the data
                current_field.message = value
            else:
                # Current field is new, create it and add it to the parent
                current_field = MessageDetailModel(
                    name=str(field),
                    message=value,
                    parent_model=parent_model,
                )
                self.beginInsertRows(current_field.parent(), row, row + 1)
                parent_model.children.append(current_field)
                self.endInsertRows()
            if isinstance(value, dict):
                current_field = self.parse_msg_dict(
                    msg=value, parent_model=current_field
                )
            self.update_field(parent_model=parent_model, new_field=current_field)
            row += 1
        return parent_model

    def update_field(
        self, parent_model: 'MessageDetailModel', new_field: 'MessageDetailModel'
    ):
        # Update the data in the model
        detail_index = parent_model.index(
            new_field.row(),
            0,
        )
        parent_model.setData(detail_index, new_field)


class MessageDetailProxySignals(QObject):
    searchForStr = Signal(str)


class MessageDetailProxy(QSortFilterProxyModel):
    """A proxy model to enable sort and filtering of the underlying MessageDetailModel."""

    def __init__(
        self,
        model: MessageDetailModel,
        *args,
        **kwargs,
    ):
        super(MessageDetailProxy, self).__init__(*args, **kwargs)

        self.setSourceModel(model)

        self.signals = MessageDetailProxySignals()

        self.signals.searchForStr.connect(self.update_search_filter)

        self.query_string = ''
        self.queryRE = re.compile(r'.*')

    @Slot(str)
    def update_search_filter(self, search_query: str):
        self.query_string = search_query
        # for now use the same query for both field and content
        self.queryRE = re.compile(search_query)
        self.invalidateFilter()

    def matches_query(self, value: str) -> bool:
        return self.queryRE.match(value) is not None or self.query_string in value

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        """Return true if row should be displayed, false otherwise."""
        model = self.sourceModel()

        # Iterate over every column to check for query
        if any(
            # Check if value matches query string (either regex or simple search)
            self.matches_query(
                str(model.index(sourceRow, column, sourceParent).data())
            )
            for column in range(len(model.columns))
        ):
            return True
        return False
