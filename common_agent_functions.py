from uagents import Context, Model
from typing import Any
from openai import OpenAI

class Request(Model):
    message: str

async def send_message_to_openai(ctx: Context, msg: Request, system_prompt: str) -> Any:
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": system_prompt
                }
            ]
            },
            {
            "role": "user",
            "content": msg.message
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

async def handle_message(ctx: Context, sender: str, msg: Request, system_prompt: str):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    
    try:
        response = await send_message_to_openai(ctx, msg, system_prompt)
        
        if response:
            await ctx.send(sender, Request(message=response))
        else:
            await ctx.send(sender, Request(message="Sorry, I couldn't process your request."))
    
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        await ctx.send(sender, Request(message="An error occurred while processing your message."))