# app/main.py

from fastapi import FastAPI

app = FastAPI(
    title="MCP Gateway",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "MCP Gateway is running."}
