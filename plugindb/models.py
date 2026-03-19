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
    description: str | None = None
    website: str | None = None
    is_free: bool = False
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


class ManufacturerListResponse(BaseModel):
    """Paginated list of manufacturers."""
    data: list[ManufacturerResponse]
    pagination: PaginatedResponse


class ManufacturerDetailResponse(BaseModel):
    """A manufacturer with its plugin list."""
    manufacturer: ManufacturerResponse
    plugins: list[PluginResponse]
    plugin_count: int


# ---------------------------------------------------------------------------
# Batch lookup
# ---------------------------------------------------------------------------

class BatchLookupRequest(BaseModel):
    """Request body for batch plugin lookup by names."""
    names: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Plugin names or aliases to look up (max 100)",
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
    top_manufacturers: list[dict] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "ok"
    version: str
    database: str = "connected"


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str | None = None


class CategoriesResponse(BaseModel):
    """Available plugin categories and subcategories."""
    categories: list[str]
    subcategories: dict[str, list[str]] = Field(default_factory=dict)
