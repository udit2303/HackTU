
# Predictive Toxicity Module — Coding Context & Guidelines

## 1. Scope

This document defines **how to implement** the Predictive Toxicity module.

It assumes:

* User authentication and authorization already exist
* User identity is available in request context
* Database, Celery, and PostGIS infrastructure already exist

This module is responsible **only** for:

* Creating predictive toxicity simulations
* Tracking their execution state
* Exposing computed toxicity risk and geometry

---

## 2. Module Boundary

All predictive toxicity logic must live under:

```
app/modules/predictive_toxicity/
```

The module must be **self-contained** and must not:

* Access other modules’ repositories directly
* Contain authentication logic
* Contain simulation execution code in HTTP routes

---

## 3. Internal Structure

Each layer has a strict role.

### router.py

* Defines HTTP routes under `/predictive-toxicity`
* Injects authenticated user and database session
* Delegates all logic to service layer
* Handles HTTP error semantics only

### service.py

* Owns simulation lifecycle
* Validates user ownership
* Creates simulations in `QUEUED` state
* Triggers asynchronous execution
* Enforces state transitions
* Assembles response data

### repository.py

* Contains all database queries
* Performs filtering by `user_id`
* Executes spatial queries and geometry serialization
* Has no business logic

### models.py

* Defines ORM models for predictive toxicity entities
* Maps exactly to PostGIS tables
* Contains no application logic

### schemas.py

* Defines request and response schemas
* Contains no ORM or database knowledge
* Represents public API contracts only

---

## 4. Routing Rules

All routes:

* Are prefixed with `/predictive-toxicity`
* Require an authenticated user
* Must enforce user ownership

Routes must be:

* Resource-oriented
* Asynchronous by design
* Deterministic in response shape

No route may:

* Execute simulation logic directly
* Block on long-running computation

---

## 5. Simulation Lifecycle Rules

A predictive toxicity simulation must follow this lifecycle:

```
QUEUED
 → RUNNING
 → POSTPROCESSING
 → COMPLETED | FAILED
```

Rules:

* Transitions are enforced in the service layer
* Completed or failed simulations are immutable
* Failed simulations remain queryable

---

## 6. User Ownership Model

* Every simulation is owned by exactly one user
* `user_id` must be stored with the simulation
* All queries must filter by `user_id`
* Unauthorized access must return `404`

Simulations must not be deleted on user deletion.

---

## 7. Asynchronous Execution Contract

* Simulation execution is performed outside the HTTP request lifecycle
* The service layer is responsible for triggering execution
* Workers read parameters from the database, not request payloads
* Results are persisted atomically

The API layer never waits for execution.

---

## 8. Data Responsibility Boundaries

### API Layer

* Validates inputs
* Returns structured responses
* Never performs computation

### Service Layer

* Orchestrates workflows
* Determines what happens and when

### Repository Layer

* Reads and writes database state
* Performs spatial queries and transformations

### Execution Layer

* Runs scientific models
* Writes results only via persistence layer

---

## 9. Geospatial Data Rules

* All geometry is stored natively in PostGIS
* Geometry is returned as GeoJSON
* CRS is standardized to EPSG:4326
* Geometry simplification and clipping are backend responsibilities

No geospatial computation is delegated to the client.

---

## 10. Error Semantics

The module must clearly distinguish:

* Simulation not found
* Simulation still processing
* Simulation failed
* Invalid request

Error handling must be consistent and predictable.

---

## 11. Reproducibility Requirements

Each simulation must record:

* Engine name
* Engine version
* Parameter hash
* Dataset versions

This information must be exposed in read responses.

---

## 12. Design Constraints

* No cross-module imports except shared utilities
* No business logic in repositories
* No database access in routers
* No simulation logic in API handlers

All future extensions must respect these constraints.

---

## 13. Guiding Principle

> **Predictive Toxicity is a user-scoped, asynchronous, reproducible simulation system.**
> The API coordinates.
> The service decides.
> The worker executes.
> The database remembers.
