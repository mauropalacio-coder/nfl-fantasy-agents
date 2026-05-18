import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_claude(prompt, system_prompt=None, max_tokens=1000):
    """Envía un prompt a Claude y retorna la respuesta."""
    messages = [{"role": "user", "content": prompt}]
    
    kwargs = {
        "model": "claude-sonnet-4-5",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    
    if system_prompt:
        kwargs["system"] = system_prompt
    
    response = client.messages.create(**kwargs)
    return response.content[0].text