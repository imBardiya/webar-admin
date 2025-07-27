from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import admin

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "WebAR Backend is running."}
