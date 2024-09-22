from typing import Any
from uagents import Agent, Context, Model
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SYSTEM_PROMPT = os.getenv('A2_SYSTEM_PROMPT')
SEED = os.getenv('A2_SEED')
NAME = os.getenv('A2_NAME')
PORT = int(os.getenv('A2_PORT'))
OPPONENT_ADDRESS = os.getenv('A2_OPPONENT_ADDRESS')

agent = Agent(
    name=NAME,
    port=PORT,
    seed=SEED,
    endpoint=[f"http://127.0.0.1:{PORT}/submit"],)

class Request(Model):
    message: str

async def send_message_to_openai(ctx: Context, msg: Request) -> Any:
    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": SYSTEM_PROMPT
                }
            ]
            }
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "text"
        }
    )
    response_text = response.choices[0].message.content
    ctx.logger.info(f"Response: {response_text}")
    return response_text

# This decorator tells the agent how to handle messages that match the 'Request' type. It will execute everytime a message is received.
@agent.on_message(model=Request)
async def handle_message(ctx: Context, sender: str, msg: Request):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    
    try:
        response = await send_message_to_openai(ctx, msg)
        
        # Process the response
        if response:
            # The response is already a string, so we can use it directly
            await ctx.send(sender, Request(message=response))
        else:
            await ctx.send(sender, Request(message="Sorry, I couldn't process your request."))
    
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        await ctx.send(sender, Request(message="An error occurred while processing your message."))


# @agent.on_interval(period=10000.0)
# async def send_message(ctx: Context):
#     address = OPPONENT_ADDRESS
#     if address:
#         await ctx.send(address, Request(message="Hello from {NAME}"))
#         ctx.logger.info(f"Message has been sent from {NAME}")

if __name__ == "__main__":
    print(f"agent2_address:{agent.address}")
    agent.run()
