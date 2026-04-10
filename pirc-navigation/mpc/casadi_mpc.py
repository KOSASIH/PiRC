#!/usr/bin/env python3
import casadi as ca
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

class CasADIMPC(Node):
    def __init__(self):
        super().__init__('casadi_mpc')
        
        # MPC Parameters
        self.N = 20  # Horizon
        self.dt = 0.1  # Timestep
        self.v_max = 1.0
        self.w_max = 2.0
        
        # State: [x, y, theta, v]
        self.nx = 4
        self.nu = 2  # [accel, angular_accel]
        
        # Create MPC solver
        self.setup_mpc()
        
        # ROS
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.goal_sub = self.create_subscription(PoseStamped, '/goal_pose', self.goal_callback, 10)
        
        self.current_state = np.zeros(self.nx)
        self.goal_pose = np.array([0.0, 0.0, 0.0])
        
    def setup_mpc(self):
        # Decision variables
        X = ca.SX.sym('X', self.nx, self.N+1)
        U = ca.SX.sym('U', self.nu, self.N)
        P = ca.SX.sym('P', self.nx + 3)  # Current state + goal
        
        # Cost function
        cost = 0
        for k in range(self.N):
            state_err = X[:3,k] - P[3:6]
            cost += ca.mtimes(state_err.T, state_err) + ca.mtimes(U[:,k].T, U[:,k])
        
        # Dynamics (bicycle model)
        f = lambda x, u: np.array([
            x[2] * ca.cos(x[2]) * self.dt,
            x[2] * ca.sin(x[2]) * self.dt,
            x[3] * self.dt,
            u[0] * self.dt
        ])
        
        # Constraints
        g = []
        for k in range(self.N):
            xk = X[:,k]
            uk = U[:,k]
            g.append(xk[3] - self.v_max)  # Velocity constraint
            g.append(-xk[3])               # Reverse constraint
            
        # NLP
        prob = {'f': cost, 'x': ca.vertcat(*[X.reshape((-1,1)), U.reshape((-1,1))]), 
                'p': P, 'g': ca.vertcat(*g)}
        opts = {'ipopt.print_level': 0, 'print_time': 0}
        self.solver = ca.nlpsol('solver', 'ipopt', prob, opts)
    
    def odom_callback(self, msg):
        self.current_state = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            2 * np.arctan2(msg.pose.pose.orientation.z, msg.pose.pose.orientation.w),
            np.linalg.norm([msg.twist.twist.linear.x, msg.twist.twist.angular.z])
        ])
    
    def goal_callback(self, msg):
        self.goal_pose = np.array([
            msg.pose.position.x,
            msg.pose.position.y,
            2 * np.arctan2(msg.pose.orientation.z, msg.pose.orientation.orientation.w)
        ])
    
    def solve_mpc(self):
        # Solve MPC
        x0 = np.zeros((self.nx * (self.N+1) + self.nu * self.N, 1))
        p = np.concatenate([self.current_state, self.goal_pose])
        
        sol = self.solver(x0=x0, p=p)
        u_opt = sol['x'][self.nx*(self.N+1):].full().flatten()[:2]
        
        # Publish control
        cmd = Twist()
        cmd.linear.x = np.clip(u_opt[0], -self.v_max, self.v_max)
        cmd.angular.z = np.clip(u_opt[1], -self.w_max, self.w_max)
        self.cmd_pub.publish(cmd)

def main():
    rclpy.init()
    mpc = CasADIMPC()
    rclpy.spin(mpc)
    rclpy.shutdown()
