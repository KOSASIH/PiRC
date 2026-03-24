# src/pirc/irc/client.py
"""IRC "!forward 50" → robot motors"""
import re
from typing import Dict, Any
from pirc.tge.fsm import TGEStateMachine

class PiRCClient:
    CMD_PATTERNS = {
        r'!(\w+)\s*(\d+)?': 'motion',
        r'!state\s+(\w+)': 'mission',
        r'!vision': 'toggle_vision',
        r'!emergency': 'estop',
    }
    
    def __init__(self, irc_channel: str, fsm: TGEStateMachine):
        self.channel = irc_channel
        self.fsm = fsm
    
    async def handle_message(self, user: str, message: str):
        for pattern, handler in self.CMD_PATTERNS.items():
            match = re.match(pattern, message)
            if match:
                await self._dispatch(user, handler, match.groups())
    
    async def _dispatch(self, user: str, cmd: str, args: tuple):
        if cmd == 'motion':
            speed = int(args[1]) if args[1] else 50
            self.fsm.set_action(f"MOVE_FORWARD_{speed}")
            await self.channel.send(f"@{user} Robot moving at {speed}%")
