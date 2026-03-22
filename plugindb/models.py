"""Pydantic response models for the PluginDB API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Core resource models
# ---------------------------------------------------------------------------

class ManufacturerResponse(BaseModel):
    """A plugin manufacturer / company."""
    id: int
    slug: str
    name: str
    website: str | None = None
    created_at: str


class PluginResponse(BaseModel):
    """A single audio plugin with full detail."""
    id: int
    slug: str
    name: str
    manufacturer: ManufacturerResponse
    category: str
    subcategory: str | None = None
    formats: list[str] = Field(default_factory=list)
    daws: list[str] = Field(default_factory=list)
    os: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    description: str | None = None
    website: str | None = None
    image_url: str | None = None
    manual_url: str | None = None
    is_free: bool = False
    price_type: str = "paid"
    year: int | None = None
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    """Pagination metadata included in list responses."""
    total: int
    page: int
    per_page: int
    pages: int


class PluginListResponse(BaseModel):
    """Paginated list of plugins."""
    data: list[PluginResponse]
    total: int = 0
    pagination: PaginatedResponse
    related_tags: dict[str, int] | None = None


class ManufacturerWithCountResponse(ManufacturerResponse):
    """A manufacturer with its plugin count."""
    plugin_count: int = 0


class ManufacturerListResponse(BaseModel):
    """Paginated list of manufacturers with plugin counts."""
    data: list[ManufacturerWithCountResponse]
    pagination: PaginatedResponse


class ManufacturerDetailResponse(BaseModel):
    """A manufacturer with its paginated plugin list."""
    manufacturer: ManufacturerResponse
    plugins: list[PluginResponse]
    plugin_count: int
    categories: dict[str, int] = Field(default_factory=dict)
    pagination: PaginatedResponse | None = None


# ---------------------------------------------------------------------------
# Batch lookup
# ---------------------------------------------------------------------------

class BatchLookupRequest(BaseModel):
    """Request body for batch plugin lookup by names."""
    names: list[str] = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Plugin names or aliases to look up (max 200)",
    )


class BatchLookupMatch(BaseModel):
    """A single match from a batch lookup."""
    query: str
    matched: bool
    plugin: PluginResponse | None = None


class BatchLookupResponse(BaseModel):
    """Response for batch plugin lookup."""
    results: list[BatchLookupMatch]
    matched: int
    unmatched: int
    duplicates: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stats / Health / Errors
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    """Database-wide statistics."""
    total_plugins: int
    total_manufacturers: int
    total_aliases: int
    categories: dict[str, int] = Field(default_factory=dict)
    formats: dict[str, int] = Field(default_factory=dict)
    os: dict[str, int] = Field(default_factory=dict)
    tags: dict[str, int] = Field(default_factory=dict)
    price_types: dict[str, int] = Field(default_factory=dict)
    top_manufacturers: list[dict] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "ok"
    version: str
    database: str = "connected"
    plugin_count: int | None = None
    manufacturer_count: int | None = None
    data_version: str | None = None
    uptime_seconds: float | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str | None = None


class CategoriesResponse(BaseModel):
    """Available plugin categories and subcategories."""
    categories: list[str]
    subcategories: dict[str, list[str]] = Field(default_factory=dict)


class TagsResponse(BaseModel):
    """All distinct tags with usage counts."""
    tags: dict[str, int] = Field(default_factory=dict)
    total: int = 0


class FormatsResponse(BaseModel):
    """All plugin formats with usage counts."""
    formats: dict[str, int] = Field(default_factory=dict)
    total: int = 0


class OSResponse(BaseModel):
    """All operating systems with usage counts."""
    os: dict[str, int] = Field(default_factory=dict)
    total: int = 0


class SubcategoriesResponse(BaseModel):
    """Subcategories with actual plugin counts from the database."""
    subcategories: dict[str, dict[str, int]] = Field(default_factory=dict)


class SuggestItemResponse(BaseModel):
    """A single autocomplete suggestion with context."""
    name: str
    slug: str
    category: str
    manufacturer_name: str
    image_url: str | None = None


class SuggestResponse(BaseModel):
    """Autocomplete suggestions."""
    suggestions: list[str] = Field(default_factory=list)
    results: list[SuggestItemResponse] = Field(default_factory=list)
    query: str


class ComparisonResponse(BaseModel):
    """Side-by-side plugin comparison."""
    plugins: list[PluginResponse]
    comparison: dict = Field(default_factory=dict)


class YearsResponse(BaseModel):
    """Plugin counts by release year."""
    years: dict[int, int] = Field(default_factory=dict)
    total: int = 0
