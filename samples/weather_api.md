# Project Specification: weather-api

## What
A small REST API that returns current weather data for a given city, wrapping the Open-Meteo API.

## Who
Developers learning API development or needing a simple backend to test against.

## Problem
Open-Meteo is powerful but raw. A thin wrapper with a clean JSON schema and caching makes it easy to consume.

## Key Features
- `GET /weather?city=<name>` — returns temperature, wind speed, weather description
- City name resolved to lat/lon via Open-Meteo geocoding endpoint
- In-memory cache (60-second TTL) to avoid redundant upstream calls
- Structured JSON error responses (missing param, city not found, upstream failure)
- Health check endpoint: `GET /health`

## Constraints
- Python 3.10+
- `fastapi` + `uvicorn` for the HTTP layer
- `httpx` for upstream HTTP calls
- No database — cache is in-memory only
- Must include at least one integration test using `httpx.AsyncClient`

## Out of Scope
- Authentication or API keys for callers
- Historical weather data
- Persistent caching (Redis, etc.)
- Deployment configuration
