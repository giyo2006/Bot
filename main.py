import time
import hmac
import hashlib
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# ENV variables (use Railway Variables or .env locally)
MAIN_API_KEY = os.getenv("MAIN_API_KEY")
MAIN_API_SECRET = os.getenv("MAIN_API_SECRET")

BASE_URL = "https://api.bybit.com"

app = FastAPI()

def sign(params, api_secret):
    sorted_params = sorted(params.items())
    query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)
    return hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_open_contracts(symbol="TRXUSDT"):
    endpoint = "/v2/private/position/list"
    url = BASE_URL + endpoint

    params = {
        "api_key": MAIN_API_KEY,
        "symbol": symbol,
        "timestamp": str(int(time.time() * 1000))
    }
    params["sign"] = sign(params, MAIN_API_SECRET)

    response = requests.get(url, params=params)
    data = response.json()

    try:
        contracts = float(data["result"][0]["size"])
        return contracts
    except Exception as e:
        return f"Error: {e} | Response: {data}"

@app.get("/contracts")
def contracts():
    contracts_open = get_open_contracts()
    return {"open_contracts": contracts_open
