import logging

from python_qt_binding.QtCore import (
    Qt,
    QModelIndex,
    Slot,
    QTimer,
)
from python_qt_binding.QtWidgets import (
    QLabel,
    QLineEdit,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QToolBar,
)

from rqt_topic.models.message import MessageModel
from rqt_topic.models.message_detail import MessageDetailModel, MessageDetailProxy
from rqt_topic.models.message_list import MessageListModel, MessageListProxy
from rqt_topic.models.topic_list import TopicListModel, TopicListProxy
from rqt_topic.models.topic import TopicModel

from rqt_topic.views.message_detail import MessageDetailView
from rqt_topic.views.message_list import MessageListView
from rqt_topic.views.topic_list import TopicListView

from rqt_topic.buttons.toggle_pause import TogglePause
from rqt_topic.buttons.clear import Clear as ClearAll
from rqt_topic.buttons.hide_timestamps import HideTimestamps
from rqt_topic.buttons.toggle_highlight import ToggleHighlight
from rqt_topic.buttons.resize_columns import ResizeColumns

import rclpy

log = logging.getLogger('rqt_topic')


QUEUE_SIZE_LIMIT = 1e6


class QueueSizeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel('Message list queue size:')
        self.input = QLineEdit()
        self.input.setText('100')

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)


class SearchWidget(QWidget):
    def __init__(self):
        super(SearchWidget, self).__init__()

        self.input = QLineEdit()
        self.input.setPlaceholderText('Search')
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.input)


class TopicWidget(QWidget):
    """
    main class inherits from the ui window class.

    You can specify the topics that the topic pane.

    TopicWidget.start must be called in order to update topic pane.
    """

    def __init__(self, node, plugin=None):
        super(TopicWidget, self).__init__()
        self.node = node
        self._plugin = plugin

        self.layout = QVBoxLayout(self)

        # Top-level toolbar
        self.toolbar = QToolBar('My main toolbar')
        self.layout.addWidget(self.toolbar)

        self.toggle_pause_action = TogglePause(style=self.style())
        # Connect pause button to this widgets method so we can pause / remove the workers
        self.toggle_pause_action.triggered.connect(self.toggle_pause)

        self.clear_all_action = ClearAll(style=self.style())
        self.clear_all_action.triggered.connect(self.clear_all)

        self.toggle_hide_timestamps_action = HideTimestamps(style=self.style())
        self.toggle_hide_timestamps_action.triggered.connect(self.toggle_hide)

        self.toggle_highlighting_action = ToggleHighlight(style=self.style())
        self.toggle_highlighting_action.triggered.connect(self.toggle_highlight)

        self.resize_columns_action = ResizeColumns(style=self.style())
        self.resize_columns_action.triggered.connect(self.resize_columns)

        self.toolbar.addAction(self.toggle_pause_action)
        self.toolbar.addAction(self.clear_all_action)
        self.toolbar.addAction(self.toggle_hide_timestamps_action)
        self.toolbar.addAction(self.toggle_highlighting_action)
        self.toolbar.addAction(self.resize_columns_action)

        self.queue_size_widget = QueueSizeWidget()
        self.toolbar.addWidget(self.queue_size_widget)
        self.queue_size_widget.input.textChanged.connect(self.queue_size_changed)

        self.search_bar = SearchWidget()
        self.toolbar.addWidget(self.search_bar)
        self.search_bar.input.textChanged.connect(self.search_query_changed)

        self.topic_list_model = TopicListModel(window_id=self.winId(), topics=[])
        self.topic_list_proxy = TopicListProxy(model=self.topic_list_model)
        self.topic_list_view = TopicListView(parent=self, model=self.topic_list_proxy)

        self.message_list_model = MessageListModel(messages=[])
        self.message_list_proxy = MessageListProxy(model=self.message_list_model)
        self.message_list_view = MessageListView(
            parent=self, model=self.message_list_proxy
        )

        # update message list with default queue size
        self.message_list_model.signals.updateQueueSize.emit(
            int(self.queue_size_widget.input.text())
        )

        self.message_detail_model = MessageDetailModel(name='message', message={})
        self.message_detail_proxy = MessageDetailProxy(
            model=self.message_detail_model, parent=self
        )
        self.message_detail_view = MessageDetailView(
            parent=self, model=self.message_detail_proxy
        )

        self.top_splitter = QSplitter(Qt.Vertical)
        self.top_splitter.addWidget(self.topic_list_view)
        self.top_splitter.addWidget(self.message_list_view)
        self.top_splitter.setStretchFactor(1, 1)

        self.bottom_splitter = QSplitter(Qt.Vertical)
        self.bottom_splitter.addWidget(self.top_splitter)
        self.bottom_splitter.addWidget(self.message_detail_view)
        self.bottom_splitter.setStretchFactor(1, 1)

        self.layout.addWidget(self.bottom_splitter)

        # Search for topics at 2Hz (see `start` method below)
        self.search_for_topics_timer = QTimer(self)
        self.search_for_topics_timer.timeout.connect(self.refresh_topics)

        # Connect message list view with message detail view
        self.message_list_view.clicked.connect(self.message_to_detail)

        # Cache topics being monitored before hitting pause
        self.topics_being_monitored = []

    def start(self):
        """Call this method to start updating the topic pane."""
        self.search_for_topics_timer.start(500)

    def shutdown_plugin(self):
        pass

    def save_settings(self, plugin_settings, instance_settings):
        pass

    def restore_settings(self, pluggin_settings, instance_settings):
        pass

    def toggle_hide(self):
        if self.toggle_hide_timestamps_action.is_hidden():
            self.topic_list_view.setColumnHidden(
                self.topic_list_model.columns.index('timestamp'), True
            )
            self.message_list_view.setColumnHidden(
                self.message_list_model.columns.index('timestamp'), True
            )
        else:
            self.topic_list_view.setColumnHidden(
                self.topic_list_model.columns.index('timestamp'), False
            )
            self.message_list_view.setColumnHidden(
                self.message_list_model.columns.index('timestamp'), False
            )

    def toggle_highlight(self):
        if self.toggle_highlighting_action.is_highlighting():
            self.topic_list_model.highlight_new_messages = True
            self.message_list_model.highlight_new_messages = True
        else:
            self.topic_list_model.highlight_new_messages = False
            self.message_list_model.highlight_new_messages = False

    def resize_columns(self):
        self.message_list_view.resizeColumnsToContents()
        self.message_list_view.horizontal_header.setStretchLastSection(True)

        self.topic_list_view.resizeColumnsToContents()

    def clear_all(self):
        self.message_detail_model.clear()
        self.message_list_model.clear()
        self.topic_list_model.clear()
        self.message_list_view.clearSelection()

    def toggle_pause(self):
        if self.toggle_pause_action.is_paused():
            self.pause()
        else:
            self.resume()

    def pause(self):
        """Pause all topic workers."""
        self.topics_being_monitored = []
        for topic_name, topic_worker in self.topic_list_model.workers.items():
            if topic_worker.topic in self.topic_list_model.topics:
                topic_worker.topic.monitor = False
                topic_worker.stop()
                self.topics_being_monitored.append(topic_worker.topic)
                log.info(f'Paused worker for topic `{topic_worker.topic.name}`')

        if not self.topic_list_model.monitoring():
            [
                self.topic_list_model.delete_topic_worker(topic)
                for topic in self.topics_being_monitored
            ]

    def resume(self):
        """Resume all topic workers."""
        for topic in self.topics_being_monitored:
            topic.monitor = True
            self.topic_list_model.create_topic_worker(topic)
            self.topic_list_model.update_topic(topic)
            log.info(f'Resuming worker for topic `{topic.name}`')

    @Slot()
    def refresh_topics(self):
        """Search for topics and if found, update topics model and view."""
        available_topics = self.node.get_topic_names_and_types() if rclpy.ok() else []
        listed_topics = self.topic_list_model.available_topics()
        if available_topics != listed_topics:
            self.topic_list_model.topics = []
            # Create the topic models
            for name, msg_type in available_topics:
                new_topic = TopicModel(
                    name=name,
                    message_type=msg_type[0],
                )
                self.topic_list_model.update_topic(new_topic)

        # Connect all active topic workers to the message list model
        for topic_name, topic_worker in self.topic_list_model.workers.items():
            # Only connect the signal if it isnt already connected
            update_message_meta_method = topic_worker.signals.metaObject().method(6)
            # Assert here in case code changes in the future, adjust method number ^
            assert update_message_meta_method.name() == 'update_message'
            if not topic_worker.signals.isSignalConnected(update_message_meta_method):
                topic_worker.signals.update_message.connect(self.update_messages)

    @Slot(MessageModel)
    def update_messages(self, msg: MessageModel):
        self.message_list_model.signals.addMessage.emit(msg)
        self.message_list_proxy.invalidateFilter()

        one_subscription_or_one_topic_selected = any(
            [
                self.topic_list_model.monitoring_count() == 1,
                self.topic_list_view.topic_is_selected(msg.topic),
            ]
        )
        if (
            not self.message_list_view.selectedIndexes()
            and one_subscription_or_one_topic_selected
        ):
            self.message_detail_model.signals.updateMsg.emit(msg.content)

    @Slot(QModelIndex)
    def message_to_detail(self, index):
        model = index.model()
        # Translate the sort/filter index to the source model index so we get the right row
        source_index = model.mapToSource(index)
        row = source_index.row()
        self.message_detail_model.update(model.sourceModel().messages[row].content)

    @Slot(str)
    def queue_size_changed(self, queue_size_txt: str):
        # Validate input queue size
        if not queue_size_txt:
            queue_size_txt = '1'
        queue_size_int = int(queue_size_txt)
        if queue_size_int > QUEUE_SIZE_LIMIT:
            log.error(
                f'Given queue size {queue_size_int} is too large (> {QUEUE_SIZE_LIMIT})'
            )
            queue_size_int = QUEUE_SIZE_LIMIT
        self.message_list_model.signals.updateQueueSize.emit(queue_size_int)

    @Slot(str)
    def search_query_changed(self, query_text: str):
        self.message_list_proxy.signals.searchForStr.emit(query_text)
        self.message_detail_proxy.signals.searchForStr.emit(query_text)
