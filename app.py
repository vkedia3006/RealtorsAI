import requests
from fastapi import FastAPI, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

FB_APP_ID = "636664199191003"
FB_APP_SECRET = "db457a2ea5cf9a2112e7e79bcf95115e"
FB_REDIRECT_URI = "https://4e8d-199-247-192-103.ngrok-free.app"
VERIFY_TOKEN = "mysecrettoken123"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WebhookData(BaseModel):
    object: str
    entry: list
    
@app.get("/")
async def read_root():
    return {"message": "Welcome to the homepage!"}    

@app.get("/api/test")
async def test():
    print("HELLO WORLD")
    return "Hello World!"

@app.get("/callback")
async def facebook_callback(code: str):
    """Handles OAuth callback and exchanges code for an access token."""
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "redirect_uri": FB_REDIRECT_URI,
        "code": code
    }

    response = requests.get(token_url, params=params)
    data = response.json()

    return data if "access_token" in data else {"error": "Failed to get access token", "details": data}

@app.post("/webhooks")
async def facebook_webhook(data: WebhookData):
    """Handles incoming webhook events from Facebook."""
    print("Received webhook:", data.dict())
    return {"status": "received"}

@app.get("/webhooks")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: int = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """Facebook Webhook Verification."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return JSONResponse(content={"hub.challenge": hub_challenge}, status_code=status.HTTP_200_OK)

    return JSONResponse(content={"error": "Invalid token"}, status_code=status.HTTP_403_FORBIDDEN)