# API-Development-Standards (FastAPI)

**Purpose**: Define a consistent, simple, and enforceable way to build REST APIs for the Dynamic Hazard Early Warning System (EWS)
**Audience**: All backend developers
**Prerequisites**:

* Module Structure & Boundaries Guideline
* Repository & ORM Rules Guideline
* Authentication & JWT Guideline

**Last Updated**: 2026-01-31

---

## Table of Contents

1. Overview
2. Core Philosophy
3. When to Use This Pattern
4. Implementation Guidelines
5. Typed Contracts & Enums
6. API Routes — Detailed Request & Response Contracts
7. Error Contracts
8. Anti-Patterns
9. Testing Recommendations
10. Related Guidelines

---

## 1. Overview

This document defines the **standard way to create API endpoints** in this FastAPI project for the **Dynamic Hazard Early Warning System (EWS)**.

The API layer is a **thin, stateless wrapper** over AI/ML models that perform:

* Ground stability analytics
* Landslide & subsidence prediction
* Scenario-based simulations (e.g. heavy rainfall)
* Risk heatmap generation
* Evacuation intelligence

All processing, evaluation, and decision logic is performed by the **model layer**.

---

## 2. Core Philosophy

### Thin Router, Thin Service, Fat Model

* **Routers**

  * Define HTTP routes only
  * Bind request and response schemas
  * No logic, no conditionals

* **Services**

  * Orchestrate data flow
  * Call models and repositories
  * No mathematical or scoring logic

* **Models**

  * Perform all analytics and prediction
  * Treated as black boxes by API layer

* **Schemas**

  * Define all API contracts
  * Enforce strict typing
  * Power Swagger documentation

---

## 3. When to Use This Pattern

### Use this pattern when:

* Exposing model inference via REST
* Returning numerical risk outputs
* Returning GeoJSON data
* Accepting `area_id` as input

### Do NOT use this pattern when:

* Training models
* Writing background jobs
* Writing ETL pipelines

---

## 4. Implementation Guidelines

### Module Structure

```
app/modules/<module_name>/
├── router.py
├── service.py
├── schemas.py
├── repository.py   # optional
```

Rules:

* Routers → Services → Models / Repositories
* No cross-module imports at router level
* Models are never called from routers

---

## 5. Typed Contracts & Enums

All shared types and enums **must live in**:

```
app/core/types/
```

### Core Enums

```python
class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"
```

```python
class HazardType(str, Enum):
    LANDSLIDE = "landslide"
    SUBSIDENCE = "subsidence"
```

```python
class TimeHorizon(str, Enum):
    HOURS_6 = "6h"
    HOURS_24 = "24h"
    HOURS_72 = "72h"
    DAYS_7 = "7d"
```

```python
class HeatmapLayer(str, Enum):
    LANDSLIDE_RISK = "landslide_risk"
    SUBSIDENCE_RISK = "subsidence_risk"
    SOIL_MOISTURE = "soil_moisture"
    DISPLACEMENT_RATE = "displacement_rate"
```

```python
class HeatmapResolution(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

```python
class SimulationType(str, Enum):
    RAINFALL = "rainfall"
    SOIL_SATURATION = "soil_saturation"
    GROUNDWATER_RISE = "groundwater_rise"
    LOAD_INCREASE = "load_increase"
```

---

## 6. API Routes — Detailed Request & Response Contracts

### 6.1 Analytics

#### Route

```
POST /analytics
```

#### Request — `AnalyticsRequest`

```json
{
  "area_id": "string",
  "time_range": {
    "from_time": "ISO-8601 datetime",
    "to_time": "ISO-8601 datetime"
  }
}
```

#### Response — `AnalyticsResponse`

```json
{
  "stability_index": 0.46,
  "confidence": 0.91,
  "metrics": {
    "soil_moisture_avg": 0.63,
    "displacement_trend_mm_per_month": 3.8,
    "rainfall_accumulation_mm": 402
  }
}
```

---

### 6.2 Prediction

#### Route

```
POST /predict
```

#### Request — `PredictionRequest`

```json
{
  "area_id": "string",
  "hazard": "landslide",
  "horizon": "72h"
}
```

#### Response — `PredictionResponse`

```json
{
  "hazard": "landslide",
  "risk_score": 0.84,
  "risk_level": "high",
  "confidence": 0.88,
  "expected_window": {
    "from_time": "2026-02-02T10:00:00Z",
    "to_time": "2026-02-03T20:00:00Z"
  }
}
```

---

### 6.3 Scenario Simulation

#### Route

```
POST /scenario
```

#### Request — `ScenarioRequest`

```json
{
  "area_id": "string",
  "hazard": "landslide",
  "scenarios": [
    {
      "type": "rainfall",
      "total_mm": 250,
      "duration_hours": 24
    },
    {
      "type": "groundwater_rise",
      "rise_meters": 1.2
    }
  ]
}
```

#### Response — `ScenarioResponse`

```json
{
  "baseline_risk": 0.38,
  "results": [
    {
      "scenario_type": "rainfall",
      "risk_score": 0.69,
      "risk_level": "high",
      "risk_delta": 0.31
    },
    {
      "scenario_type": "groundwater_rise",
      "risk_score": 0.58,
      "risk_level": "moderate",
      "risk_delta": 0.20
    }
  ]
}
```

---

### 6.4 Heatmaps

#### Route

```
POST /heatmap
```

#### Request — `HeatmapRequest`

```json
{
  "area_id": "string",
  "hazard": "landslide",
  "layer": "landslide_risk",
  "resolution": "medium"
}
```

#### Response — `HeatmapResponse` (GeoJSON)

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...]]]
      },
      "properties": {
        "risk_score": 0.81,
        "risk_level": "high"
      }
    }
  ]
}
```

---

### 6.5 Evacuation

#### Route

```
POST /evacuation
```

#### Request — `EvacuationRequest`

```json
{
  "area_id": "string",
  "start_points": [
    { "lat": 26.91, "lon": 75.79 }
  ]
}
```

#### Response — `EvacuationResponse`

```json
{
  "routes": [
    {
      "route_id": "route_1",
      "risk_score": 0.14,
      "eta_minutes": 17,
      "geometry": {
        "type": "LineString",
        "coordinates": [[75.79, 26.91], [...]]
      }
    }
  ]
}
```

---

## 7. Error Contracts

Standard error format:

```json
{
  "detail": "Error message"
}
```

Rules:

* Use `HTTPException`
* Do not expose stack traces
* Do not leak model internals

---

## 8. Anti-Patterns

❌ Free-text scenario parameters
❌ Accepting geometry instead of `area_id`
❌ Business logic in routers
❌ Mathematical logic in services
❌ Untyped JSON payloads

---

## 9. Testing Recommendations

* Validate request/response schemas
* Mock models in service tests
* Validate enum serialization
* Validate GeoJSON compliance
* Do not test model internals at API level

---

## 10. Related Guidelines

* Module Structure & Boundaries
* Repository & ORM Rules
* Authentication & JWT
* Model Versioning
* Error Handling

---

## Changelog

| Date       | Changes                                         | Author |
| ---------- | ----------------------------------------------- | ------ |
| 2026-01-31 | Full typed EWS API standards with I/O contracts | System |

---