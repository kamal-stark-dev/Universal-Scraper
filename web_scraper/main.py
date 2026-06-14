from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


class ScrapeRequest(BaseModel):
    url: str
    extract: list[str]


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        {"request": request},
        "index.html",
    )


@app.post("/scrape")
def scrape(data: ScrapeRequest):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            data.url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "lxml"
        )

        result = {}

        if "headings" in data.extract:
            headings = []

            for tag in soup.find_all(
                ["h1", "h2", "h3", "h4", "h5", "h6"]
            ):
                text = tag.get_text(strip=True)

                if text:
                    headings.append(text)

            result["headings"] = headings

        if "paragraphs" in data.extract:
            paragraphs = []

            for p in soup.find_all("p"):
                text = p.get_text(strip=True)

                if text:
                    paragraphs.append(text)

            result["paragraphs"] = paragraphs

        if "links" in data.extract:
            links = []

            for a in soup.find_all("a", href=True):
                links.append(
                    urljoin(data.url, a["href"])
                )

            result["links"] = links

        if "images" in data.extract:
            images = []

            for img in soup.find_all("img"):
                src = img.get("src")

                if src:
                    images.append(
                        urljoin(data.url, src)
                    )

            result["images"] = images

        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )