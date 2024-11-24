import uvicorn

from sources.Controllers.config import PORT

if __name__ == "__main__":
    uvicorn.run(
        "sources:app", host="localhost", port=int(PORT), reload=True
    )
