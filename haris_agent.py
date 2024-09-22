from uagents import Agent, Context
from common_agent_functions import Request, handle_message
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = os.getenv('A1_SYSTEM_PROMPT')
SEED = os.getenv('A1_SEED')
NAME = os.getenv('A1_NAME')
PORT = int(os.getenv('A1_PORT'))
OPPONENT_ADDRESS = os.getenv('A1_OPPONENT_ADDRESS')

agent = Agent(
    name=NAME,
    port=PORT,
    seed=SEED,
    endpoint=[f"http://127.0.0.1:{PORT}/submit"],
)

@agent.on_message(model=Request)
async def haris_handle_message(ctx: Context, sender: str, msg: Request):
    await handle_message(ctx, sender, msg, SYSTEM_PROMPT)

@agent.on_interval(period=10000.0)
async def send_message(ctx: Context):
    if OPPONENT_ADDRESS:
        await ctx.send(OPPONENT_ADDRESS, Request(message=f"Hello from {NAME}"))
        ctx.logger.info(f"Message has been sent from {NAME}")

if __name__ == "__main__":
    print(f"Haris agent address: {agent.address}")
    agent.run()
