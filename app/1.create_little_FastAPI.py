from fastapi import FastAPI
app = FastAPI(title = 'fastapi todo demo')
@app.get("/health")
def healtg_check():
    return {"status": "ok"}
