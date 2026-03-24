# src/pirc/tge/fsm.py
"""Hierarchical FSM + PyTrees3 - Production Ready"""
from py_trees import BehaviourTree
from py_trees.composites import Sequence, Parallel
from py_trees.decorators import Timeout
from dataclasses import dataclass
from typing import Optional, Dict, Any
import asyncio
import json

@dataclass
class RobotState:
    battery: float
    pose: Dict[str, float]
    objects: Dict[str, list]
    mission: str

class TGEStateMachine:
    def __init__(self):
        self.global_state = "IDLE"
        self.context = RobotState(battery=1.0, pose={}, objects={}, mission="PATROL")
        self.sub_trees: Dict[str, BehaviourTree] = {}
        
    async def update(self, sensors) -> Dict[str, Any]:
        """Main TGE tick"""
        self.context = sensors.state
        
        # Global mission FSM
        if self._global_transition(sensors):
            await self._switch_mission()
        
        # Execute tactical BT
        bt = self.sub_trees[self.global_state]
        result = bt.tick()
        
        return {
            "action": bt.status,
            "next_state": self.global_state,
            "debug": bt.node_outputs
        }
