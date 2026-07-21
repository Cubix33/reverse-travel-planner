from typing import Literal

from pydantic import BaseModel, Field


class TripPreferences(BaseModel):
    budget_inr: int = Field(ge=5000, le=500000)
    days: int = Field(ge=2, le=30)
    starting_city: str = "Delhi"
    passport: str = "Indian"
    travel_styles: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    pace: Literal["slow", "moderate", "fast"] = "moderate"
    weather_min_c: int = 10
    weather_max_c: int = 30
    companion: Literal["solo", "friends", "family", "partner"] = "solo"
    max_flight_hours: float = Field(default=8.0, ge=1.0, le=30.0)
    experience_query: str | None = None


class DimensionScore(BaseModel):
    label: str
    score: int


class MatchReason(BaseModel):
    positive: list[str]
    negative: list[str]


class DestinationMatch(BaseModel):
    id: str
    name: str
    country: str
    region: str
    tagline: str
    match_percent: int
    dimensions: list[DimensionScore]
    reasons: MatchReason
    hidden_gems: list[str]
    estimated_total_inr: int
    flight_hours: float
    visa_status: str
    avg_temp_c: int
    budget_breakdown: dict[str, int]
    trip_dna: dict[str, int]
    genome_highlights: dict[str, int]


class RecommendResponse(BaseModel):
    matches: list[DestinationMatch]
    trip_dna: dict[str, int]
    query_summary: str


class ExperienceSearchRequest(BaseModel):
    query: str
    starting_city: str = "Delhi"
    passport: str = "Indian"
    budget_inr: int = 50000
    days: int = 5
    max_flight_hours: float = 12.0


class ExplainRequest(BaseModel):
    destination_id: str
    preferences: TripPreferences


class ItineraryRequest(BaseModel):
    destination_id: str
    preferences: TripPreferences


class CompareRequest(BaseModel):
    destination_ids: list[str] = Field(min_length=2, max_length=3)
    preferences: TripPreferences


class ActivityItem(BaseModel):
    time: str
    title: str
    note: str


class ItineraryDay(BaseModel):
    day: int
    title: str
    focus: str
    activities: list[ActivityItem]


class ConciergeTip(BaseModel):
    trigger: str
    action: str


class ItineraryResponse(BaseModel):
    destination_id: str
    destination_name: str
    summary: str
    days: list[ItineraryDay]
    concierge: list[ConciergeTip]
    packing_tips: list[str]
    source: str
