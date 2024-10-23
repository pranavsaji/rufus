# rufus/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import asyncio
from .client import RufusClient

app = FastAPI(
    title="Rufus API",
    description="Intelligent Web Data Extraction for RAG Systems",
    version="0.2.0"
)

class ScrapeRequest(BaseModel):
    url: str
    instructions: str
    keywords: Optional[List[str]] = None

class ScrapeResponse(BaseModel):
    url: str
    content: str

@app.post("/scrape", response_model=List[ScrapeResponse])
async def scrape_endpoint(request: ScrapeRequest):
    """
    Endpoint to initiate web scraping.

    :param request: ScrapeRequest containing the URL, instructions, and optional keywords.
    :return: List of ScrapeResponse containing URLs and extracted content.
    """
    client = RufusClient(
        base_url=request.url,
        instructions=request.instructions,
        keywords=request.keywords,
        max_depth=3,
        max_pages=100,
        similarity_threshold=0.3
    )
    try:
        results = await client.scrape(request.url, request.instructions)
        if not results:
            raise HTTPException(status_code=404, detail="No relevant documents were extracted.")
        return results
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run("rufus.api:app", host="0.0.0.0", port=8000, reload=True)
