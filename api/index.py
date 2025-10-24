
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI  # type: ignore  # type: ignore
from dotenv import load_dotenv
import os
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials

load_dotenv()  # loads variables from .env

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
print('clerk_config')
print(clerk_config)
clerk_guard = ClerkHTTPBearer(clerk_config)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]  # User ID from JWT - available for future use
    # We now know which user is making the request! 
    # You could use user_id to:
    # - Track usage per user
    # - Store generated ideas in a database
    # - Apply user-specific limits or customization
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = [{"role": "user", "content": "Come up with a new business idea for AI Agents"}]
    stream = client.chat.completions.create(model="gpt-4o-mini", messages=prompt, stream=True)

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines:
                    yield f"data: {line}\n"
                yield "\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")