from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class AskRequest(StrictModel):
    question: str = Field(min_length=3, max_length=1200)

class SearchArgs(StrictModel):
    query: str = Field(min_length=2, max_length=300)

class ArticleArgs(StrictModel):
    article_id: str = Field(min_length=1, max_length=80, pattern=r'^[a-z][a-z0-9-]+$')

class Answer(StrictModel):
    status: Literal['answered', 'insufficient_evidence']
    answer: str = Field(min_length=1, max_length=6000)
    citations: list[str] = Field(max_length=6)

    @model_validator(mode='after')
    def valid_citation_shape(self):
        if len(set(self.citations)) != len(self.citations):
            raise ValueError('Duplicate citations')
        if (self.status == 'answered') != bool(self.citations):
            raise ValueError('Answered responses need citations; abstentions must have none')
        return self
