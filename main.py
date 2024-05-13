from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Mount a static directory for serving CSS and JavaScript files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chatbot", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})


class ChatInput(BaseModel):
    message: str


# Chatbot

@app.post("/chatbot")
def get_response(input_data: ChatInput):
    user_message = input_data.message
    print(user_message)
