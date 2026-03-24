# src/pirc/__main__.py
"""pirc run --robot=donkey --irc=#robotwars"""
import asyncio
import click
import structlog
from pirc.core.scheduler import PiRCScheduler
from pirc.tge.fsm import TGEStateMachine
from pirc.irc.client import PiRCClient
from pirc.api.server import create_app

logger = structlog.get_logger()

@click.command()
@click.option('--robot', default='donkey')
@click.option('--irc', default='#pirc')
def main(robot: str, irc: str):
    """🚀 Launch PiRC Robot + IRC Control"""
    async def startup():
        # 1. Start FastAPI API
        app = create_app()
        api_task = asyncio.create_task(
            asyncio.to_thread(lambda: uvicorn.run(app, host="0.0.0.0", port=8000))
        )
        
        # 2. Robot Core (50Hz)
        scheduler = PiRCScheduler()
        fsm = TGEStateMachine()
        robot_task = asyncio.create_task(scheduler.run(fsm))
        
        # 3. IRC Client (chat control)
        irc_client = PiRCClient(irc_channel=irc)
        irc_task = asyncio.create_task(irc_client.connect())
        
        await asyncio.gather(api_task, robot_task, irc_task)
    
    asyncio.run(startup())

if __name__ == "__main__":
    main()
