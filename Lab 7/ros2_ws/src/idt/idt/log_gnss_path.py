#!/usr/bin/env python3



import rclpy
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile
from mavros_msgs.msg import GPSRAW
from sensor_msgs.msg import NavSatFix
import datetime
import time

def format_csv_line(arr):
    return ", ".join(map(str, arr)) + "\n"

class ros_node_class(Node):
    def __init__(self):
        super().__init__('log_gnss_path')

        now = datetime.datetime.now().strftime("%S-%M-%H-%d-%m-%Y")

        self.global_pos_file = open(f"./global_pos_{now}.csv", 'a')
        self.raw_fix_file = open(f"./raw_fix_{now}.csv", 'a')
        self.gps1_raw_file = open(f"./gps1_raw_{now}.csv", 'a')
        
        self.time_start = time.time()

        # publishers

        # subscribers
        self.sub_global_pos = self.create_subscription(
            NavSatFix,                             # message type
            '/mavros/global_position/global',      # topic to subscribe to
            self.on_global_pos_msg,                # callback function
            QoSProfile(depth=10,reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.sub_global_pos_raw = self.create_subscription(
            NavSatFix, # message type
            '/mavros/global_position/raw/fix', # topic to subscribe to
            self.on_global_pos_raw_msg, # callback function 
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        self.sub_gpsstatus_gps1_raw = self.create_subscription(
            GPSRAW, # message type
            '/mavros/gpsstatus/gps1/raw', # topic to subscribe to
            self.on_gpstatus_gps1_raw_msg, # callback function 
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        # timers
        self.timer = self.create_timer(5.0, self.timer_update)
 
    def on_global_pos_msg(self, msg):
        self.get_logger().info('/mavros/global_position/global (FC estimate): %.6f %.6f %.3f WGS84'
                               % (msg.latitude, msg.longitude, msg.altitude))
        
        self.global_pos_file.write(format_csv_line([self.time(), msg.latitude, msg.longitude, msg.altitude]))
        
    def time(self):
        return time.time() - self.time_start

    def on_global_pos_raw_msg(self, msg):
        if msg.status.status == -1:
            fix = "No fix"
        else:
            fix = "Fix ok"
        self.get_logger().info('/mavros/global_position/raw/fix (GNSS raw): %s %.6f %.6f %.3f WGS84'
                               % (fix, msg.latitude, msg.longitude, msg.altitude))
        self.raw_fix_file.write(format_csv_line([self.time(), msg.status.status, msg.latitude, msg.longitude, msg.altitude]))

    def on_gpstatus_gps1_raw_msg(self, msg):
        if msg.fix_type == 0:
            fix = "No fix"
        else:
            fix = "Fix ok"
        self.get_logger().info('/mavros/gpsstatus/gps1/raw (GNSS raw): %s %.6f %.6f %.3f AMSL'
                               % (fix, msg.lat/10000000.0, msg.lon/10000000.0, msg.alt/1000.0))
        self.gps1_raw_file.write(format_csv_line([self.time(), msg.fix_type, msg.lat/10000000.0, msg.lon/10000000.0, msg.alt/1000.0]))

    def timer_update(self):
        self.get_logger().info('Timer update')

def main(args=None):
    rclpy.init(args=args)
    ros_node = ros_node_class()
    rclpy.spin(ros_node)

    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
