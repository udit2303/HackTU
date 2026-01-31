# API-Development-Standards (FastAPI)

**Purpose**: Define a consistent, simple, and enforceable way to build REST APIs in this FastAPI project  
**Audience**: All backend developers  
**Prerequisites**:
- Module Structure & Boundaries Guideline
- Repository & ORM Rules Guideline
- Authentication & JWT Guideline

**Last Updated**: 2026-01-31

---

## Table of Contents

1. Overview  
2. Core Philosophy  
3. When to Use This Pattern  
4. Implementation Guidelines  
5. Request, Response & Error Contracts  
6. Code Examples  
7. Anti-Patterns  
8. Testing Recommendations  
9. Related Guidelines  

---

## Overview

This document defines the **standard way to create API endpoints** in this FastAPI project.

The goal is to ensure that all APIs are:

- Predictable
- Consistent across modules
- Fully validated
- Automatically documented (Swagger)
- Easy to refactor and extend

This guideline is intentionally **simple and opinionated** to avoid ambiguity and architectural drift.

---

## Core Philosophy

### Thin Router, Fat Service

- **Routers**
  - Define HTTP routes only
  - Bind request and response schemas
  - Never contain business logic

- **Services**
  - Contain all business logic
  - Enforce validation and rules
  - Coordinate repositories and utilities

- **Repositories**
  - Handle database access only
  - ORM-only (SQLAlchemy / GeoAlchemy2)
  - No business logic

- **Schemas (Pydantic)**
  - Validate input and output
  - Define API contracts
  - Power Swagger documentation

---

## When to Use This Pattern

### Use this pattern when:
- Creating any HTTP API endpoint
- Adding CRUD operations for a module
- Exposing business logic over REST
- Creating authenticated or protected routes

### Do NOT use this pattern when:
- Writing background jobs
- Writing CLI scripts
- Writing database migrations
- Writing shared utilities

---

## Implementation Guidelines

### Step 1: Choose the Module

Every API endpoint belongs to **exactly one module**.

```

app/modules/<module_name>/
├── router.py
├── service.py
├── repository.py
├── models.py
├── schemas.py

````

Rules:
- Routers only talk to services
- Services may talk to multiple repositories
- Repositories never talk to other repositories
- Cross-module access **must go through services**

---

### Step 2: Define Schemas (Pydantic)

All endpoints **must** use Pydantic schemas.

#### Input Schema Example

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
````

#### Response Schema Example

```python
class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
```

Rules:

* Never accept `dict`, `Any`, or raw JSON
* Never return ORM models directly
* Sensitive fields must never appear in response schemas

---

### Step 3: Implement Router

Routers define HTTP endpoints and nothing else.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.modules.users import service, schemas
from app.deps import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=201,
)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    return service.create_user(db, payload)
```

Rules:

* No business logic
* No database queries
* Always use dependency injection
* Always use schemas

---

### Step 4: Implement Service

Services contain all business logic.

```python
from app.modules.users import repository
from app.core.security import hash_password
from fastapi import HTTPException, status

def create_user(db, payload):
    if repository.user_exists(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    hashed = hash_password(payload.password)
    return repository.create_user(db, payload.email, hashed)
```

Rules:

* Password hashing belongs here
* Authorization checks belong here
* Validation beyond schema-level belongs here
* Transactions are coordinated here

---

### Step 5: Implement Repository

Repositories are responsible for data access only.

```python
from app.modules.users.models import User

def create_user(db, email, password):
    user = User(email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

Rules:

* ORM-only (SQLAlchemy / GeoAlchemy2)
* No raw SQL
* No business logic
* No cross-module table access

---

### Step 6: Authentication & Authorization

Protected endpoints must use JWT-based dependencies.

```python
from fastapi import Depends
from app.core.security import get_current_user

@router.get("/me")
def get_me(user = Depends(get_current_user)):
    return user
```

Rules:

* User context always comes from JWT
* Never trust user IDs from request body or query params
* Authorization checks belong in the service layer

---

## Request, Response & Error Contracts (Mandatory)

Every API endpoint must explicitly define:

1. Request schema
2. Response schema
3. Success status code
4. Possible error responses

---

### Request Contracts

Rules:

* Every endpoint must declare a request schema (except GET without body)
* Never accept raw dictionaries or untyped input
* Validation must fail fast

```python
@router.post("/")
def create_user(payload: UserCreate):
    ...
```

---

### Response Contracts

Rules:

* Always declare `response_model`
* Never return ORM objects directly
* Only return fields defined in the schema

```python
@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
)
def create_user(...):
    ...
```

---

### HTTP Status Codes

Endpoints must use **appropriate HTTP status codes** explicitly.

| Scenario                 | Status Code |
| ------------------------ | ----------- |
| Successful GET           | 200         |
| Successful POST (create) | 201         |
| Successful PATCH         | 200         |
| Successful DELETE        | 204         |
| Validation error         | 422         |
| Authentication required  | 401         |
| Authorization failure    | 403         |
| Resource not found       | 404         |
| Conflict                 | 409         |
| Internal error           | 500         |

---

### Error Handling Rules

* Errors must be raised using `HTTPException`
* Never return error dictionaries manually
* Error logic belongs in the **service layer**

```python
raise HTTPException(
    status_code=404,
    detail="User not found",
)
```

---

### Documenting Error Responses

Important error responses must be declared in the router.

```python
@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    responses={
        409: {"description": "User already exists"},
        401: {"description": "Authentication required"},
    },
)
```

---

### Standard Error Response Shape

FastAPI error format:

```json
{
  "detail": "Error message"
}
```

Rules:

* Do not override this format
* Do not expose stack traces
* Error messages must be user-safe

---

## Anti-Patterns (What NOT to Do)

### ❌ Business Logic in Routers

```python
# BAD
if payload.price < 0:
    raise HTTPException(...)
```

```python
# GOOD
return service.create(payload)
```

---

### ❌ Cross-Module Database Access

```python
# BAD
db.query(User).filter(...)
```

```python
# GOOD
users_service.get_user(...)
```

---

### ❌ Raw SQL Queries

```python
# BAD
db.execute("SELECT * FROM users")
```

```python
# GOOD
db.query(User)
```

---

### ❌ Skipping Schemas

```python
# BAD
def create(data: dict):
```

```python
# GOOD
def create(data: UserCreate):
```
---

## Related Guidelines

* Module Structure & Boundaries
* Repository & ORM Rules
* Authentication & JWT
* Database Migrations
* Error Handling

---

## Changelog

| Date       | Changes                       | Author |
| ---------- | ----------------------------- | ------ |
| 2026-01-31 | Initial FastAPI API standards | System |

