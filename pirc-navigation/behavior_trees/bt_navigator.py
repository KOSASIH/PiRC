#!/usr/bin/env python3
import py_trees
import rclpy
from rclpy.node import Node
from py_trees_ros.actions import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class BTNavigator(Node):
    def __init__(self):
        super().__init__('bt_navigator')
        
        # Behavior Tree
        self.tree = self.create_behavior_tree()
        self.tree.tick_tock(period_ms=100)
    
    def create_behavior_tree(self):
        root = py_trees.composites.Sequence(name="Root")
        
        # High-level behaviors
        check_battery = py_trees_ros.actions.ActionClient(
            name="CheckBattery",
            action_type=NavigateToPose,
            action_server="battery_check"
        )
        
        local_nav = py_trees_ros.actions.ActionClient(
            name="LocalNavigation",
            action_type=NavigateToPose,
            action_server="navigate_to_pose"
        )
        
        obstacle_avoid = py_trees_ros.actions.ActionClient(
            name="ObstacleAvoid",
            action_type=NavigateToPose,
            action_server="avoid_obstacle"
        )
        
        global_plan = py_trees_ros.actions.ActionClient(
            name="GlobalPlanner",
            action_type=NavigateToPose,
            action_server="global_planner"
        )
        
        root.add_children([
            check_battery,
            global_plan,
            local_nav,
            obstacle_avoid
        ])
        
        return root

def main():
    rclpy.init()
    navigator = BTNavigator()
    rclpy.spin(navigator)
