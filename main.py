from fastapi import FastAPI

app = FastAPI()


@app.get("/timestamp")
def root():
    return "Hello"
