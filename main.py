from fastapi import FastAPI
app = FastAPI()
@app.get("/welcome")
def welcome():
    return {"message": "Welcome to FastAPI!"}
@app.get("/input")
def bye(input: str):
    return {input: "Goodbye from FastAPI!"}