from fastapi import FastAPI

app = FastAPI(
    title="Solar & Wind Deployment Intelligence Platform",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to Solar & Wind Deployment Intelligence Platform API"
    }

@app.get("/health")
def health():
    return {
        "status": "Running"
    }

@app.get("/about")
def about():
    return {
        "project": "Solar & Wind Deployment Intelligence Platform"
    }