from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Provider(BaseModel):
    name: str = Field(description="The provider name")


class TemporalCoverage(BaseModel):
    start: Optional[datetime] = Field(description="The temporal coverage start datetime")
    end: Optional[datetime] = Field(description="The temporal coverage end datetime")


class SpatialCoverage(BaseModel):
    geojson: List[Any] = Field(description="A list of Spatial Coverages in geojson format")


class Creator(BaseModel):
    name: str = Field(description="The creator name")


class CreatorList(BaseModel):
    list: List[Creator] = Field(alias="@list", default=[], description="A list of creator names")


class License(BaseModel):
    text: Optional[str] = Field(description="The license text as a string")


class Funder(BaseModel):
    name: Optional[str] = Field(description="A funder name")


class Funding(BaseModel):
    name: Optional[str] = Field(description="The name of the funding")
    number: Optional[str] = Field(description="The funding number")
    funder: Optional[Funder] = Field(description="A list of funders")


class JSONLD(BaseModel):
    context: HttpUrl = Field(alias='@context', default='https://schema.org')
    repository_identifier: Optional[str] = Field(description="The identifier used by the repository")
    url: HttpUrl = Field(description="The url to the record in the repository")
    type: str = Field(alias='@type', default='Dataset')
    provider: Provider = Field(description="The repository provider name")
    name: Optional[str] = Field(description="The name or title of the record")
    description: Optional[str] = Field(description="The description or abstract of the record")
    keywords: Optional[List[str]] = Field(description="The keywords or subjects of the record")
    creator: Optional[CreatorList] = Field(
        description="A list of the creator names of the record"
    )  # creator.@list.name
    funding: Optional[List[Funding]] = Field(description="A list of funding sources of the record")

    temporalCoverage: Optional[TemporalCoverage] = Field(description="The temporal coverage of the record")
    spatialCoverage: Optional[SpatialCoverage] = Field(description="The spatial coverage of the record")
    license: Optional[License] = Field(description="The license of the record")
    datePublished: Optional[datetime] = Field(description="The date the record was published by the repository")
    dateCreated: Optional[datetime] = Field(description="The date the record was created on the repository")
    relations: Optional[List[str]] = Field(default=[], description="A list of relationships with other records")
    legacy: Optional[bool] = Field(
        default=False, description="Indicates whether the record was submitted through the submission portal"
    )
    clusters: Optional[List[str]]

    class Settings:
        name = "discovery"


class TypeEnum(str, Enum):
    text = "text"
    hit = "hit"


class Text(BaseModel):
    value: str
    type: TypeEnum


class PathEnum(str, Enum):
    name = "name"
    description = "description"
    keywords = "keywords"
    creators = "creator.@list.name"

    @classmethod
    def values(self):
        return [e.value for e in self]


class Highlight(BaseModel):
    score: float
    path: PathEnum
    texts: List[Text]


class TypeAhead(BaseModel):
    highlights: List[Highlight]


class DiscoveryResult(JSONLD):
    score: float
    highlights: List[Highlight]
