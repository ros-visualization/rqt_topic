from datetime import datetime
from typing import TypeVar
import threading

from python_qt_binding.QtCore import QRunnable, Slot, QObject, Signal

from rclpy.node import Node
import rclpy.serialization
from ros2topic.verb.bw import ROSTopicBandwidth
from ros2topic.verb.hz import ROSTopicHz
from rqt_py_common.message_helpers import get_message_class

from rqt_topic.models.topic import TopicModel
from rqt_topic.models.message import MessageModel

MsgType = TypeVar("MsgType")


MAX_HZ = 60.0  # Hz
MAX_HZ_AS_SECONDS = 1 / MAX_HZ  # seconds


class TopicWorkerSignals(QObject):
    """
    Plain QObject-derived class to hold the signals used by the QRunnable.

    Signals are only supported for QObject-derived objects.
    """

    # start = Signal(TopicModel)
    # stop = Signal(TopicModel)
    update_topic = Signal(TopicModel)
    update_message = Signal(MessageModel)


class TopicWorker(QRunnable):
    """
    Meant to handle all work related to fetching data from a single topic.

    Runs in a separate thread than the main GUI to avoid GUI-lock and to
    update as soon as new data is available.

    Each worker has one node with one subscription to completely seperate everything.
    """

    def __init__(self, window_id: int, topic: TopicModel, *args, **kwargs):
        super(TopicWorker, self).__init__()

        self.window_id = int(window_id)

        # Initialize node
        self.node = Node(
            f"rqt_topic_worker_node_{self.window_id}_{topic.name.replace('/', '_')}"
        )
        self.topic = topic
        self.signals = TopicWorkerSignals()
        self.subscriber = None
        self.ros_topic_hz = ROSTopicHz(self.node, 100)
        self.ros_topic_bw = ROSTopicBandwidth(self.node, 100)
        self.message_class = get_message_class(topic.message_type)

        # self.signals.start.connect(self.run)
        # self.signals.stop.connect(self.stop)

        # Use a MultiThreadedExecutor
        self.executor = rclpy.executors.MultiThreadedExecutor()
        self.executor.add_node(self.node)

        # To be filled in the `run` method
        self.executor_thread = None

        self.last_message_updated_at = datetime.now()

    @Slot()
    def run(self):
        """
        Create subscriptin to the specified topic.

        Meant to be called in its own seperate thread via QThreadpool.
        """
        if self.executor_thread is None or not self.executor_thread.is_alive():
            # Spin node in its own thread
            self.executor_thread = threading.Thread(
                target=self.executor.spin, daemon=True
            )
            self.executor_thread.start()

        self.subscriber = self.node.create_subscription(
            self.message_class, self.topic.name, self.impl, qos_profile=10, raw=True
        )

    @Slot()
    def stop(self):
        """Stop and remove the current subscription."""
        self.node.destroy_subscription(self.subscriber)
        self.subscriber = None
        self.executor.shutdown()
        self.executor_thread = None

    def impl(self, data):
        self.topic.timestamp = datetime.now()

        msg = rclpy.serialization.deserialize_message(
            data,
            self.message_class,
        )

        # Parse msg fields into a simple nested dictionary (converts arrays and sequences
        # to strings)
        # This avoids passing large arrays / sequences around to other models and views here
        self.topic.message = MessageModel(
            timestamp=self.topic.timestamp,
            topic=self.topic.name,
            message_type=self.topic.message_type,
            content=self.recursively_parse_message(msg),
        )

        self.ros_topic_hz.callback_hz(msg, self.topic.name)
        self.ros_topic_bw.callback(data)

        bw_tuple = self.ros_topic_bw.get_bw()
        if bw_tuple:
            self.topic.bandwidth.fill(
                bw_tuple[0], bw_tuple[1], bw_tuple[2], bw_tuple[3], bw_tuple[4]
            )

        hz_tuple = self.ros_topic_hz.get_hz(self.topic.name)
        if hz_tuple:
            self.topic.frequency.fill(
                hz_tuple[0],
                hz_tuple[1],
                hz_tuple[2],
                hz_tuple[3],
                hz_tuple[4],
            )

        if self.topic.frequency.rate == 0.0 or self.topic.frequency.rate > MAX_HZ:
            # Throttle updating the GUI since most monitors cannot refresh faster than 60Hz anyways
            time_since_last_publish = datetime.now() - self.last_message_updated_at
            if time_since_last_publish.total_seconds() >= MAX_HZ_AS_SECONDS:
                self.signals.update_topic.emit(self.topic)
                self.signals.update_message.emit(self.topic.message)
                self.last_message_updated_at = datetime.now()
        else:
            # If frequence is below limit, refresh GUI at rate that messages are available
            self.signals.update_topic.emit(self.topic)
            self.signals.update_message.emit(self.topic.message)

    def recursively_parse_message(
        self, msg_content: MsgType, content_type_str: str = ""
    ):
        """
        Parse a given message into a nested dictionary of its fields.

        First call to this function expects a raw rclpy message class that has
        the `get_fields_and_field_types` method
        """
        contents = {}
        if hasattr(msg_content, "get_fields_and_field_types"):
            fields_and_types = msg_content.get_fields_and_field_types()
            contents = {
                field: self.recursively_parse_message(
                    msg_content=getattr(msg_content, field), content_type_str=type_str
                )
                for field, type_str in fields_and_types.items()
            }
        else:
            type_str, array_size = self.extract_array_info(content_type_str)

            if array_size is None:
                return msg_content

            if "/" not in type_str and array_size:
                # This is a sequence, so just display type instead of data: `sequence<type, size>`
                return content_type_str

            try:
                msg_class = get_message_class(type_str)()
            except (ValueError, TypeError):
                msg_class = None

            if hasattr(msg_class, "__slots__"):
                contents = {
                    index: self.recursively_parse_message(
                        msg_content=msg_class,
                        content_type_str=type_str,
                    )
                    for index in range(int(array_size))
                }
        return contents

    def extract_array_info(self, type_str):
        """
        This converts a given array or sequence type string into a human readable string.

        By doing this we avoid storing large arrays and sequences since this tool is not meant for
        that (e.g. image data, pointcloud data, etc.)
        """
        array_size = None
        if "[" in type_str and type_str[-1] == "]":
            type_str, array_size_str = type_str.split("[", 1)
            array_size_str = array_size_str[:-1]
            if len(array_size_str) > 0:
                array_size = int(array_size_str)
            else:
                array_size = 0
        elif type_str.startswith("sequence<") and type_str.endswith(">"):
            type_str_sanitized = type_str[9:-1]
            # type str may or may not include bounds
            if "," in type_str_sanitized:
                type_str, array_size = type_str[9:-1].split(", ")
            else:
                type_str = type_str_sanitized
                array_size = "0"

        return type_str, array_size
