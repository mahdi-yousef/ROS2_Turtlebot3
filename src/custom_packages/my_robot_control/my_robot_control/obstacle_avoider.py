#!/usr/bin/env python3
"""
obstacle_avoider.py

A reactive, LiDAR-based obstacle avoidance node for TurtleBot3.

Behavior scheme (classic "bug"-style reactive control):
  - Look at a forward cone of the LaserScan.
  - If nothing is closer than STOP_DISTANCE, drive forward.
  - If something is closer, stop and rotate toward the side with more open
    space (compare the mean range on the left half of the scan vs. the
    right half).
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ObstacleAvoider(Node):

    def __init__(self):
        super().__init__('obstacle_avoider')

        self.declare_parameter('stop_distance', 0.45)      # meters
        self.declare_parameter('forward_speed', 0.15)       # m/s
        self.declare_parameter('turn_speed', 0.6)           # rad/s
        self.declare_parameter('forward_cone_deg', 40.0)    # +/- degrees around front

        self.stop_distance = self.get_parameter('stop_distance').value
        self.forward_speed = self.get_parameter('forward_speed').value
        self.turn_speed = self.get_parameter('turn_speed').value
        self.forward_cone_deg = self.get_parameter('forward_cone_deg').value

        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, qos_profile_sensor_data)

        self.get_logger().info(
            f'obstacle_avoider started: stop_distance={self.stop_distance} m, '
            f'forward_speed={self.forward_speed} m/s'
        )

    def scan_callback(self, msg: LaserScan):
        n = len(msg.ranges)
        if n == 0:
            return

        def valid(r):
            return r if (msg.range_min < r < msg.range_max) and not math.isinf(r) else float('inf')

        ranges = [valid(r) for r in msg.ranges]

        cone_count = max(1, int(self.forward_cone_deg / (360.0 / n)))
        front = ranges[:cone_count] + ranges[-cone_count:]
        front_min = min(front) if front else float('inf')

        cmd = Twist()

        if front_min > self.stop_distance:
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0
        else:
            left = ranges[: n // 2]
            right = ranges[n // 2:]
            left_avg = sum(r for r in left if r != float('inf')) / max(
                1, len([r for r in left if r != float('inf')]))
            right_avg = sum(r for r in right if r != float('inf')) / max(
                1, len([r for r in right if r != float('inf')]))

            cmd.linear.x = 0.0
            cmd.angular.z = self.turn_speed if left_avg > right_avg else -self.turn_speed

            self.get_logger().debug(
                f'Obstacle at {front_min:.2f} m -> turning '
                f'{"left" if left_avg > right_avg else "right"}'
            )

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
