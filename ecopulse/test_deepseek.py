import os
import asyncio
import httpx

async def test_openrouter():
    API_KEY = "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"  # Replace with your actual key
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "EcoPulse",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [
            {
                "role": "user",
                "content": "How can I conserve energy at home?"
            }
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("🔄 Calling OpenRouter API...")
            response = await client.post(API_URL, headers=headers, json=payload)
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"Response: {result['choices'][0]['message']['content']}")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())