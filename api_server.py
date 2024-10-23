# api_server.py

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
from rufus import RufusClient

app = FastAPI(
    title="Rufus API",
    description="API for Rufus Web Data Extraction Tool",
    version="1.0.0"
)

# Pydantic models for request and response
class ScrapeRequest(BaseModel):
    base_url: str
    instructions: str
    keywords: Optional[List[str]] = None
    max_depth: int = 2
    max_pages: int = 50
    similarity_threshold: float = 0.5

class ScrapeResponse(BaseModel):
    url: str
    content: str

# Dependency for API Key authentication
def get_api_key(x_api_key: str = Header(...)):
    expected_api_key = os.getenv('RUFUS_API_KEY')
    if x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return x_api_key

@app.post("/scrape", response_model=List[ScrapeResponse])
async def scrape_data(request: ScrapeRequest, api_key: str = Depends(get_api_key)):
    """
    Endpoint to scrape data from a website based on provided instructions.
    """
    try:
        client = RufusClient(
            api_key=api_key,
            instructions=request.instructions,
            keywords=request.keywords,
            max_depth=request.max_depth,
            max_pages=request.max_pages,
            similarity_threshold=request.similarity_threshold
        )
        results = await client.scrape(request.base_url)
        if not results:
            raise HTTPException(status_code=404, detail="No relevant documents were extracted.")
        return results
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during scraping.")

# Optional: Root endpoint for health check
@app.get("/")
async def read_root():
    return {"message": "Rufus API is up and running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)


