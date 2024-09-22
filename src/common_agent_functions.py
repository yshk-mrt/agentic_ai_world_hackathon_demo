import logging

# httpxのログレベルを警告以上に設定
logging.getLogger("httpx").setLevel(logging.WARNING)

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
        max_tokens=128,
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

async def handle_message_common(ctx: Context, sender: str, msg: Request, system_prompt: str, name: str):
    
    try:
        response = await send_message_to_openai(ctx, msg, system_prompt)
        
        response_msg = f"{msg.message}\n\n{name}: {response}"
        
        await ctx.send(sender, Request(message=response_msg), sync=True)
    
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        await ctx.send(sender, Request(message="An error occurred while processing your message."), sync=True)