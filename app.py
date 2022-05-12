from json import load

from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi.extension import Limiter
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def handle_rate_limit(request: Request, error: RateLimitExceeded):
    response = JSONResponse(
        {"message": f"Rate limit exceeded: {error.detail}"}, status_code=429
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response


with open("levels.json", "r") as f:
    data = load(f)


def respond(message: str, **kwargs):
    return {"message": message, **kwargs}


@app.get("/")
def home():
    return "Hello there! This API was built by Dorukyum for the event team of TCR. To solve a level: GET /{level}?answer={answer}"


@app.get("/{level}")
@limiter.limit("24/minute")
def level(request: Request, level: int, answer: str):
    try:
        current_data = data[str(level)]
    except KeyError:
        return respond("There is no such level.")
    if current_data["answer"] == answer:
        if (next_data := data.get(str(level + 1))) and (
            next_hint := next_data.get("hint")
        ):
            return respond("Success!", next_hint=next_hint)
        return respond(current_data["message"])
    return respond("Incorrect answer.")
