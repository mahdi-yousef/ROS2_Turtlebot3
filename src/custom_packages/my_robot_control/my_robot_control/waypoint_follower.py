#!/usr/bin/env python3
"""
waypoint_follower.py

Sends a sequence of (x, y, yaw) goals to Nav2's NavigateToPose action, one at
a time, waiting for each to complete before sending the next.

Waits for AMCL to publish a localized pose (/amcl_pose) before sending the
first goal -- this is what makes the node safe to run automatically inside
nav_demo.launch.py: without this, goals would be sent (and rejected) the
moment Nav2's action server exists, before an initial pose estimate has
been given in RViz.
"""

import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose


def yaw_to_quaternion(yaw: float):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class WaypointFollower(Node):

    def __init__(self):
        super().__init__('waypoint_follower')

        self.declare_parameter('waypoints', [0.0])  # overridden via YAML/launch
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('wait_for_localization', True)

        flat = self.get_parameter('waypoints').value
        self.frame_id = self.get_parameter('frame_id').value
        self.wait_for_localization = self.get_parameter('wait_for_localization').value

        if len(flat) < 3 or len(flat) % 3 != 0:
            self.get_logger().error(
                'waypoints parameter must be a flat list of (x, y, yaw) triples. '
                'Falling back to a single demo waypoint at (1.0, 0.0, 0.0).'
            )
            flat = [1.0, 0.0, 0.0]

        self.waypoints = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
        self.current_index = 0
        self._localized = not self.wait_for_localization

        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        if self.wait_for_localization:
            self.get_logger().info(
                'waypoint_follower waiting for AMCL localization '
                '(give a "2D Pose Estimate" in RViz)...'
            )
            self._amcl_sub = self.create_subscription(
                PoseWithCovarianceStamped, 'amcl_pose', self._on_amcl_pose, 1)
        else:
            self._start()

    def _on_amcl_pose(self, msg):
        if self._localized:
            return
        self._localized = True
        self.get_logger().info('AMCL pose received -- starting waypoint mission.')
        self.destroy_subscription(self._amcl_sub)
        self._start()

    def _start(self):
        self.get_logger().info(
            f'waypoint_follower ready with {len(self.waypoints)} waypoint(s). '
            'Waiting for Nav2 action server...'
        )
        self._client.wait_for_server()
        self.send_next_goal()

    def send_next_goal(self):
        if self.current_index >= len(self.waypoints):
            self.get_logger().info('All waypoints reached. Mission complete.')
            return

        x, y, yaw = self.waypoints[self.current_index]
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = self.frame_id
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        _, _, qz, qw = yaw_to_quaternion(yaw)
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.get_logger().info(
            f'Sending waypoint {self.current_index + 1}/{len(self.waypoints)}: '
            f'x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}'
        )

        send_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        send_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        remaining = feedback_msg.feedback.distance_remaining
        self.get_logger().debug(f'Distance remaining: {remaining:.2f} m')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected by Nav2. Skipping to next waypoint.')
            self.current_index += 1
            self.send_next_goal()
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        status = future.result().status
        if status == 4:  # SUCCEEDED per action_msgs/GoalStatus
            self.get_logger().info(f'Waypoint {self.current_index + 1} reached.')
        else:
            self.get_logger().warn(
                f'Waypoint {self.current_index + 1} did not succeed (status={status}).'
            )
        self.current_index += 1
        self.send_next_goal()


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
