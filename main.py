from fastapi import FastAPI

app = FastAPI()
app.title = "Mi aplicacion con FastAPI"
app.version = "0.0.1"

@app.get('/', tags=['home'])
def message():
    return "Hello world"