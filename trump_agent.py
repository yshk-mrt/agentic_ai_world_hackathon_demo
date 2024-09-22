from uagents import Agent, Context
from common_agent_functions import Request, handle_message
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = os.getenv('A2_SYSTEM_PROMPT')
SEED = os.getenv('A2_SEED')
NAME = os.getenv('A2_NAME')
PORT = int(os.getenv('A2_PORT'))
OPPONENT_ADDRESS = os.getenv('A2_OPPONENT_ADDRESS')

agent = Agent(
    name=NAME,
    port=PORT,
    seed=SEED,
    endpoint=[f"http://127.0.0.1:{PORT}/submit"],
)

@agent.on_message(model=Request)
async def trump_handle_message(ctx: Context, sender: str, msg: Request):
    await handle_message(ctx, sender, msg, SYSTEM_PROMPT)

if __name__ == "__main__":
    print(f"Trump agent address: {agent.address}")
    agent.run()