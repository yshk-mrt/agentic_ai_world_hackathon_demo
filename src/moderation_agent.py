import json
import os
from dotenv import load_dotenv
import requests
from toolhouse import Toolhouse
from groq import Groq
from uagents import Agent, Context
from common_agent_functions import Request, handle_message_common

load_dotenv()

SYSTEM_PROMPT = os.getenv('A0_SYSTEM_PROMPT')
SEED = os.getenv('A0_SEED')
NAME = os.getenv('A0_NAME')
A1_NAME = os.getenv('A1_NAME')
A2_NAME = os.getenv('A2_NAME')
PORT = int(os.getenv('A0_PORT'))
A0_ADDRESS = os.getenv('A0_ADDRESS')
A1_ADDRESS = os.getenv('A2_OPPONENT_ADDRESS')
A2_ADDRESS = os.getenv('A1_OPPONENT_ADDRESS')
TOPIC = "Which party will have more generous policy for the international students?"

agent = Agent(
    name=NAME,
    port=PORT,
    seed=SEED,
    endpoint=[f"http://127.0.0.1:{PORT}/submit"],
)

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
MODEL = "llama3-groq-70b-8192-tool-use-preview"

th = Toolhouse()
messages = [{
    "role": "user",
    "content": SYSTEM_PROMPT + "\n\nParticipants: " + A1_NAME + ", " + A2_NAME + "\n\nTopic:" + TOPIC
}]

@th.register_local_tool("moderate_discussion")
def moderate_discussion(
   participant: str, 
   statement: str,
   reasoning: str) -> str:
   #print(f"Moderation: Participant: {participant}, Statement: {statement}, Reasoning: {reasoning}")
   return f"participant: {participant}, statement: {statement}"

my_local_tools = [
    {
        "type": "function",
        "function": {
            "name": "moderate_discussion",
            "description": "Guides the discussion with minimal intervention, ensuring equal participation from all speakers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "participant": {
                        "type": "string",
                        "description": f"The identifier of the participant who should speak next. {A1_NAME} or {A2_NAME}",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "The rationale for selecting this participant and any guidance provided, focusing on maintaining balance and natural flow.",
                    },
                    "statement": {
                        "type": "string",
                        "description": "A brief prompt or question to guide the chosen participant, if necessary. Use 'continue' without other words to let the conversation flow naturally, or 'end' when sufficient discussion has occurred.",
                    },
                },
                "required": [
                    "participant",
                    "statement",
                    "reasoning",
                ],
            },
        },
    }
]

@agent.on_message(model=Request)
async def handle_message(ctx: Context, sender: str, msg: Request):
    # **1. エージェント自身からのメッセージを無視**
    #ctx.logger.info(f"Message received from: '{sender}'")
    if sender == A0_ADDRESS:
        #ctx.logger.info("Ignoring message from self.")
        return
    #else:
    #    ctx.logger.info(f"Message received from: '{sender}'")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": msg.message,
        }
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=my_local_tools,  # th.get_tools()
            tool_choice="required",
        )

        # レスポンスの処理
        if response.choices and response.choices[0].message:
            message = response.choices[0].message
            #print(message)
            
            if message.tool_calls:
                tool_run = th.run_tools(response)
                messages.extend(tool_run)
                #ctx.logger.info(messages)

                # 最新のツール実行結果のみを処理
                if tool_run and len(tool_run) > 0:
                    for tool_response in tool_run:
                        content = tool_response.get('content')
                        
                        if content:
                            parts = content.split('statement:')
                            if len(parts) == 2:
                                name_part = parts[0].strip()
                                statement_part = parts[1].strip()
                                name = name_part.replace('participant:', '').strip().rstrip(',')
                                response_text = statement_part

                                #ctx.logger.info(f"Extracted - Name: {name}, Statement: {response_text}")
                                ctx.logger.info(f"{NAME}: {response_text}")

                                if name and response_text:
                                    if response_text.lower() == "continue":
                                        response_text = ""
                                    else:
                                        response_text = f"Bob: {response_text}"
                                    
                                    if name == A1_NAME:
                                        await ctx.send(A1_ADDRESS, Request(message=response_text), sync=True)
                                    elif name == A2_NAME:
                                        await ctx.send(A2_ADDRESS, Request(message=response_text), sync=True)
                                    else:
                                        ctx.logger.warning(f"Unknown participant: {name}")
                                        recipient = A1_ADDRESS if sender == A2_ADDRESS else A2_ADDRESS
                                        await ctx.send(recipient, Request(message=""), sync=True)
                                else:
                                    ctx.logger.error("Failed to extract name or statement from the response.")
                                    recipient = A1_ADDRESS if sender == A2_ADDRESS else A2_ADDRESS
                                    await ctx.send(recipient, Request(message="Failed to process the response."), sync=True)
                            else:
                                ctx.logger.error(f"Unexpected format in tool response: {content}")
                        else:
                            pass#ctx.logger.error("Tool response content is missing.")
                else:
                    ctx.logger.error("No tool_run messages found.")
            else:
                # ツール呼び出しがない場合の処理
                ctx.logger.info(f"No tool called")
                recipient = A1_ADDRESS if sender == A2_ADDRESS else A2_ADDRESS
                await ctx.send(recipient, Request(message=msg.message), sync=True)
    except Exception as e:
        ctx.logger.error(f"Error processing message: {str(e)}")
        recipient = A1_ADDRESS if sender == A2_ADDRESS else A2_ADDRESS
        await ctx.send(recipient, Request(message="An error occurred while processing your request."))

@agent.on_interval(period=10000.0)
async def send_message(ctx: Context):
    msg = f"Hi {A1_NAME}, Let's talk about {TOPIC}"
    ctx.logger.info(msg)
    await ctx.send(A1_ADDRESS, Request(message=msg), sync=True)

if __name__ == "__main__":
    agent.run()