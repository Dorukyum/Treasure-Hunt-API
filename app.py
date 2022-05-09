from json import load

from fastapi import FastAPI

app = FastAPI()
with open("levels.json", "r") as f:
    data = load(f)


def respond(message: str, **kwargs):
    return {"message": message, **kwargs}


@app.get("/")
def home():
    return "Hello there! This API was built by Dorukyum for the event team of TCR. To solve a level: GET /{level}?answer={answer}"


@app.get("/{level}")
def level(level: int, answer: str):
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
