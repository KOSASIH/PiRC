#!/usr/bin/env python
"""Hello PiRC - First working demo"""
import asyncio
from pirc.core import PiRCCore

async def battery_plugin(state):
    """Dummy plugin - prints battery"""
    print(f"🔋 Battery: {state.battery:.1%} | {state.timestamp:.3f}s")

async def main():
    core = PiRCCore()
    core.register_plugin("battery", battery_plugin)
    
    # Run 10 seconds demo
    core_task = asyncio.create_task(core.run())
    await asyncio.sleep(10)
    core.running = False
    await core_task

if __name__ == "__main__":
    asyncio.run(main())
