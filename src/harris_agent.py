from uagents import Agent, Context
from common_agent_functions import Request, handle_message_common
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = os.getenv('A1_SYSTEM_PROMPT')
SEED = os.getenv('A1_SEED')
NAME = os.getenv('A1_NAME')
PORT = int(os.getenv('A1_PORT'))
A0_ADDRESS = os.getenv('A0_ADDRESS')

agent = Agent(
    name=NAME,
    port=PORT,
    seed=SEED,
    endpoint=[f"http://127.0.0.1:{PORT}/submit"],
)

@agent.on_message(model=Request)
async def handle_message(ctx: Context, sender: str, msg: Request):
    if sender != A0_ADDRESS:
        return
    #else:
    #    ctx.logger.info(f"Message received from: '{sender}'")
    
    await handle_message_common(ctx, A0_ADDRESS, msg, SYSTEM_PROMPT, NAME)

if __name__ == "__main__":
    agent.run()
