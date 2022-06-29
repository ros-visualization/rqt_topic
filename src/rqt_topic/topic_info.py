# Copyright (c) 2011, Dorian Scholz, TU Darmstadt
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
#   * Neither the name of the TU Darmstadt nor the names of its
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

from python_qt_binding.QtCore import qWarning
import rclpy.serialization
from ros2topic.verb.bw import ROSTopicBandwidth
from ros2topic.verb.hz import ROSTopicHz
from rqt_py_common.message_helpers import get_message_class


class TopicInfo:

    def __init__(self, node, topic_name, topic_type):
        self._node = node
        self._clock = self._node.get_clock()
        self._topic_name = topic_name
        self._ros_topic_hz = ROSTopicHz(node, 100)
        self._ros_topic_bw = ROSTopicBandwidth(node, 100)
        self.error = None
        self._subscriber = None
        self.monitoring = False
        self._reset_data()
        self.message_class = None
        if topic_type is None:
            self.error = 'No topic types associated with topic: ' % topic_name
        try:
            self.message_class = get_message_class(topic_type)
        except Exception as e:
            self.message_class = None
            qWarning('TopicInfo.__init__(): %s' % (e))

        if self.message_class is None:
            self.error = 'can not get message class for type "%s"' % topic_type
            qWarning('TopicInfo.__init__(): topic "%s": %s' % (topic_name, self.error))

    def _reset_data(self):
        self.last_message = None

    def toggle_monitoring(self):
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        if self.message_class is not None:
            self.monitoring = True
            self._subscriber = self._node.create_subscription(
                self.message_class, self._topic_name, self.message_callback,
                qos_profile=10, raw=True)

    def stop_monitoring(self):
        self.monitoring = False
        self._reset_data()
        if self._subscriber is not None:
            self._node.destroy_subscription(self._subscriber)
            self._subscriber = None

    def is_monitoring(self):
        return self.monitoring

    def get_hz(self):
        return self._ros_topic_hz.get_hz(self._topic_name)

    def get_last_printed_tn(self):
        return self._ros_topic_hz.get_last_printed_tn(self._topic_name)

    def message_callback(self, data):
        self.last_message = rclpy.serialization.deserialize_message(data, self.message_class)
        self._ros_topic_hz.callback_hz(self.last_message, self._topic_name)
        self._ros_topic_bw.callback(data)

    def get_bw(self):
        return self._ros_topic_bw.get_bw()
