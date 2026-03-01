import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Updated LangChain Imports
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
load_dotenv()

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_secret_token_123")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

app = Flask(__name__)

# ==========================================
# 2. LANGCHAIN TOOL (Sending Messages)
# ==========================================
@tool
def send_whatsapp_message(recipient_number: str, message_body: str) -> str:
    """
    Sends a WhatsApp text message to a specific phone number.
    Use this tool whenever you need to reply to the user.
    """
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "text": {"body": message_body}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Successfully sent message to {recipient_number}"
    except Exception as e:
        return f"Failed to send message. Error: {str(e)}"

# ==========================================
# 3. HUGGING FACE LLM & AGENT INITIALIZATION
# ==========================================
# 1. Connect to a free Hugging Face Endpoint 
llm_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct", 
    task="text-generation",
    temperature=0.1,
    max_new_tokens=512,
    do_sample=False,
)

# 2. Wrap it as a ChatModel so it supports tool calling natively
chat_model = ChatHuggingFace(llm=llm_endpoint)

# 3. Create the agent using the new v1.0 syntax
agent = create_agent(
    model=chat_model,
    tools=[send_whatsapp_message],
    system_prompt=(
        "You are a helpful, friendly AI assistant on WhatsApp. "
        "You have a tool to send messages back to the user. "
        "Whenever the user asks a question or says hello, figure out a good response, "
        "and ALWAYS use the 'send_whatsapp_message' tool to send your final answer back."
    )
)

# ==========================================
# 4. FLASK WEBHOOK ROUTES
# ==========================================
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Handle Meta's Webhook Verification
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token and mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return 'Verification token mismatch', 403

    # Handle Incoming WhatsApp Messages
    if request.method == 'POST':
        body = request.get_json()

        if body.get('object'):
            try:
                entry = body['entry'][0]
                changes = entry['changes'][0]
                value = changes['value']
                
                if 'messages' in value:
                    message = value['messages'][0]
                    sender_phone = message['from']
                    
                    if message['type'] == 'text':
                        user_text = message['text']['body']
                        print(f"\n📩 USER SAID: {user_text}")
                        print("🤖 Agent is thinking...")
                        
                        # --- TRIGGER THE NEW LANGCHAIN AGENT ---
                        # In the new API, we pass a list of messages to the agent.
                        # We dynamically inject the phone number as a system message here.
                        agent.invoke({
                            "messages": [
                                {"role": "system", "content": f"The user's phone number is: {sender_phone}"},
                                {"role": "user", "content": user_text}
                            ]
                        })
                        
            except KeyError:
                pass # Ignore status updates like "read" or "delivered"

            # Always return 200 OK immediately so Meta doesn't retry
            return jsonify({"status": "ok"}), 200

    return "Method not allowed", 405

if __name__ == '__main__':
    print("🚀 Starting LangChain + Hugging Face Bot on port 5000...")
    app.run(port=5000, debug=True)