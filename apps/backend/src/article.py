from datetime import datetime

from pydantic import BaseModel, Field


class Article(BaseModel):
    title: str = Field(description="The title of the article")
    url: str = Field(description="The URL of the article")
    publication_date: datetime | None = Field(description="The published date of the article")
    source: str = Field(description="The source of the article")
    content: str = Field(description="The content of the article")
    description: str | None = Field(description="The description of the article", default=None)
    categories: list[str] | None = Field(description="The categories of the article", default=None)
    image_url: str | None = Field(description="The image URL of the article", default=None)
