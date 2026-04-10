#!/usr/bin/env python3
import ompl
import numpy as np
from ompl import base as ob
from ompl import geometric as og

class SBPLPlanner:
    def __init__(self):
        self.setup_sbpl()
    
    def setup_sbpl(self):
        # State space: SE(2)
        self.space = ob.RealVectorStateSpace(3)
        bounds = ob.RealVectorBounds(3)
        bounds.setLow(-10.0)
        bounds.setHigh(10.0)
        self.space.setBounds(bounds)
        
        # Planner
        self.planner = og.SBL(og.PlanarRRT(self.si))
    
    def plan(self, start, goal, occupancy_grid):
        # Setup problem
        pdef = ob.ProblemDefinition(self.si)
        start_state = ob.State(self.space)
        start_state[0] = start[0]
        start_state[1] = start[1]
        start_state[2] = start[2]
        pdef.setStartAndGoalStates(start_state, goal_state)
        
        # Solve
        self.planner.solve(pdef)
        path = pdef.getSolutionPath()
        return path
