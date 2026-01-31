# NN-Module-Structure-Guideline

**Purpose**: Define and enforce a strict, scalable module-based architecture for the backend, ensuring clear ownership, separation of concerns, and safe cross-module interactions.
**Audience**: All backend developers
**Prerequisites**: None
**Last Updated**: 2026-01-31

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use This Pattern](#when-to-use-this-pattern)
3. [Implementation Guidelines](#implementation-guidelines)
4. [Code Examples](#code-examples)
5. [Anti-Patterns](#anti-patterns)
6. [Testing Recommendations](#testing-recommendations)
7. [Related Guidelines](#related-guidelines)

---

## Overview

This guideline defines the **module-based architecture** used in this backend.  
Each feature or domain concept (e.g. users, locations, auth) must live in its own isolated module with clearly defined responsibilities.

The goal is to:
- Prevent tight coupling between features
- Ensure clean ownership of data models
- Make the system easy to extend without refactoring existing code
- Avoid “god services” and cross-table spaghetti queries

Each module owns:
- Its database models
- Its repository layer (DB access)
- Its service layer (business logic)
- Its API routes

**No module may directly access another module’s database models.**  
Cross-module access must go through the owning module’s repository or service.

This architecture ensures that business rules remain centralized, reusable, and safe as the project grows.

---

## When to Use This Pattern

This pattern applies to **all backend development in this project**.

**Use this pattern when:**
- Adding a new feature or domain concept
- Creating new database tables
- Writing business logic
- Exposing API endpoints
- Accessing data owned by another module

**Do NOT use this pattern when:**
- Writing one-off scripts (outside the app runtime)
- Writing test-only helpers
- Prototyping throwaway experimental code

---

## Implementation Guidelines

### Step 1: Create a Module Folder

**What**: Every feature must live inside its own module directory  
**Why**: Enforces ownership and prevents accidental coupling  
**How**:

Each module must follow this exact structure:

```

app/modules/<module_name>/
├── router.py
├── service.py
├── repository.py
├── models.py
└── schemas.py

````

Rules:
- One module = one domain
- Do not share models across modules
- Do not skip layers

---

### Step 2: Define Ownership of Database Models

**What**: Each database table is owned by exactly one module  
**Why**: Prevents hidden dependencies and broken invariants  
**How**:

- All SQLAlchemy models must live in `models.py` of the owning module
- No other module may import these models directly

Example ownership:
- `users` module owns `User` table
- `locations` module owns `Location` table

---

### Step 3: Enforce Cross-Module Access via Repository or Service

**What**: Modules may interact, but only through defined boundaries  
**Why**: Prevents direct DB coupling and allows internal refactors  
**How**:

If Module A needs data from Module B:
- Module A **must not** import Module B’s models
- Module A **must** call Module B’s repository or service

Preferred order:
1. Repository (for simple data fetch)
2. Service (if business logic is involved)

---

### Step 4: Repository Layer Rules

**What**: Repository layer handles database access only  
**Why**: Keeps data access predictable and testable  
**How**:

Repositories:
- Query the database
- Return raw model objects or simple data structures
- Contain **no business logic**

Allowed:
- Filters
- Joins
- Sorting
- Pagination

Not allowed:
- Data transformation
- Authorization logic
- Validation logic
- Cross-module queries on foreign models

---

### Step 5: Service Layer Rules

**What**: Service layer contains all business logic  
**Why**: Centralizes rules and enables reuse  
**How**:

Services:
- Call repositories (own module or other modules)
- Perform data processing
- Enforce business rules
- Coordinate multiple repositories if needed

**All processing must happen here.**

---

### Step 6: Router Layer Rules

**What**: Routers expose HTTP endpoints  
**Why**: Keep API thin and predictable  
**How**:

Routers:
- Parse request data
- Call service functions
- Return responses
- Apply dependencies (auth, DB)

Routers must:
- Never access repositories directly
- Never contain business logic

---

### Step 7: Authentication (JWT)

**What**: JWT is the single authentication mechanism  
**Why**: Consistency and security  
**How**:

- JWT logic lives in `app/core/security.py`
- Protected routes must use:
```python
Depends(get_current_user)
````

Rules:

* No custom auth logic inside modules
* No token parsing inside services or repositories
* Auth context is passed explicitly if needed

---

### Step 8: Shared Utilities (Horizontal Approach)

**What**: Shared logic should be reusable and horizontal
**Why**: Avoid duplication and future refactors
**How**:

Utilities must live in:

```
app/core/
```

or

```
app/utils/
```

Rules:

* Utilities must not depend on specific modules
* Utilities must not import models
* Utilities must be generic and reusable

Examples:

* Date helpers
* Geo calculations
* Formatting helpers
* Token helpers

---

### Step 9: Dependency Management

**What**: All dependencies must be explicit
**Why**: Prevent runtime failures and onboarding issues
**How**:

Rules:

* Any new dependency **must** be added to `requirements.txt`
* Do not rely on transitive or optional dependencies
* Do not install packages manually without updating `requirements.txt`

---

## ORM-Only Database Access (No Raw SQL)

### Step 10: ORM-Only Database Access

**What**: All database access must be performed using the ORM (SQLAlchemy / GeoAlchemy2).  
**Why**: Ensures consistency, safety, maintainability, and alignment with the module-based architecture.  
**How**:

All database queries **must**:
- Use SQLAlchemy ORM queries
- Use GeoAlchemy2 constructs for spatial data
- Be implemented inside the repository layer only

**Raw SQL queries are strictly forbidden.**

This includes (but is not limited to):
- `db.execute("SELECT ...")`
- `text("SELECT ...")`
- Manual SQL strings
- Cursor-level access

---

### ORM Usage Rules

Repositories **must**:
- Use ORM models owned by the module
- Express queries via SQLAlchemy query builders
- Return ORM model instances or simple ORM-backed results

Allowed:
- `db.query(Model).filter(...)`
- ORM joins between models **owned by the same module**
- ORM-based filtering, sorting, and pagination

Not allowed:
- Raw SQL strings
- Cross-module joins at the SQL level
- Database-specific hacks inside queries

---

### GeoAlchemy2-Specific ORM Rules

**What**: Spatial data access must use GeoAlchemy2 abstractions.  
**Why**: Keeps spatial logic portable, safe, and consistent with ORM usage.  
**How**:

When working with spatial data:
- Use `Geometry` / `Geography` columns from GeoAlchemy2
- Use GeoAlchemy2 functions and SQLAlchemy expressions
- Keep spatial queries inside the repository layer

Allowed:
- `func.ST_DWithin(...)`
- `func.ST_Intersects(...)`
- `func.ST_Contains(...)`
- `func.ST_Distance(...)`
- ORM-level spatial filters and joins

Example:
```python
from sqlalchemy import func

db.query(Location).filter(
    func.ST_DWithin(
        Location.geom,
        point,
        radius
    )
)
````

Not allowed:

* Raw PostGIS SQL strings
* `db.execute("SELECT ST_DWithin(...)")`
* Hardcoded SRID manipulation in SQL
* Cross-module spatial joins

All spatial processing and interpretation must happen in the **service layer**, not the repository.

---

### Why Raw SQL Is Forbidden

Raw SQL:

* Breaks module ownership rules
* Bypasses repository abstraction
* Encourages cross-table coupling
* Is harder to refactor safely
* Is difficult for LLMs to reason about
* Reduces testability and portability

ORM-based access:

* Enforces ownership boundaries
* Is composable and predictable
* Is test-friendly
* Aligns with module structure
* Produces more consistent generated code

---

### Exception Policy

**There are NO exceptions by default.**

If raw SQL is ever required:

* It must be explicitly approved
* It must be documented with justification
* It must be isolated in a single repository function
* It must include clear comments explaining why ORM is insufficient

Until such approval exists:

> **Do not write raw SQL.**

---
## Database Migrations & Extension Safety

### Purpose

This project uses **Alembic** for database migrations together with **PostGIS** extensions.  
Because PostGIS installs **extension-owned tables**, special rules are required to ensure migrations remain safe and predictable.

This section defines **how migrations work**, **what is ignored**, and **what developers must never do**.

---

### How Migrations Work

- SQLAlchemy models define the **desired schema**
- Alembic compares models (`Base.metadata`) with the actual database
- Alembic generates migrations using `--autogenerate`
- Only tables defined in SQLAlchemy models are managed by Alembic

Tables not defined in models are **intentionally ignored**.

---

### Extension-Owned Tables (PostGIS)

PostGIS and related extensions (e.g. `postgis_tiger_geocoder`) create internal tables such as:

- Spatial reference tables
- Tiger geocoder lookup tables
- Loader metadata tables

These tables:
- Are owned by PostgreSQL extensions
- Must **never** be modified or dropped by migrations
- Are automatically excluded from Alembic autogeneration

**Alembic is configured to ignore all tables that are not defined in SQLAlchemy models.**

This behavior is intentional and required.

---

### Impact on Model Changes (Important)

Ignoring extension tables **does NOT affect application tables**.

Alembic will still:
- Detect new tables
- Detect column additions/removals
- Detect constraint changes
- Detect index changes
- Detect GeoAlchemy2 geometry changes

As long as:
- The table exists in SQLAlchemy models
- The model is registered in `app/db/models.py`

All schema changes will be correctly migrated.

---

### Developer Responsibilities

All developers must follow these rules:

- **Every application table must have a SQLAlchemy model**
- **Every model must be registered in `app/db/models.py`**
- **Never create tables manually in the database**
- **Never edit PostGIS or extension tables**
- **Never write raw SQL migrations that touch extension tables**
- **Always generate migrations using `alembic revision --autogenerate`**

Failure to follow these rules will result in broken migrations.

---

### Allowed vs Forbidden Actions

**Allowed**
- Adding or modifying SQLAlchemy models
- Running Alembic migrations
- Using GeoAlchemy2 ORM constructs
- Adding spatial indexes via migrations

**Forbidden**
- Dropping extension tables
- Editing PostGIS tables
- Writing raw SQL to modify extension schemas
- Manually altering database schema

---

### Why This Rule Exists

This approach:
- Prevents accidental deletion of PostGIS internals
- Keeps migrations deterministic
- Avoids environment-specific failures
- Allows safe use of PostgreSQL extensions
- Keeps the architecture LLM-friendly and predictable

---

### Summary

> Alembic manages **only what the application owns**.  
> PostgreSQL extensions manage **everything else**.

This separation is mandatory and non-negotiable.

---

## Code Examples

> **Note**: Minimal examples for illustration only.

### Example 1: Correct Cross-Module Access

```python
# locations/service.py
from app.modules.users.repository import get_user_by_id

def assign_location_to_user(db, user_id, location_data):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
```

**Full Implementation**: See `app/modules/locations/service.py`

---

### Example 2: Repository vs Service Responsibility

```python
# users/repository.py
def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()
```

```python
# users/service.py
def create_user(db, email, password):
    hashed = hash_password(password)
    return repository.create_user(db, email, hashed)
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Direct Cross-Model Access

**Problem**: Breaks module isolation and ownership
**Instead**: Use repository or service

```python
# BAD
from app.modules.users.models import User
```

```python
# GOOD
from app.modules.users.repository import get_user_by_id
```

---

### ❌ Anti-Pattern 2: Business Logic in Repository

**Problem**: Makes DB layer unpredictable
**Instead**: Move logic to service layer

```python
# BAD
def create_user(db, email, password):
    if len(password) < 8:
        raise ValueError("Weak password")
```

```python
# GOOD
def create_user(db, email, password):
    return repository.create_user(db, email, hash(password))
```

---

### ❌ Anti-Pattern 3: Missing Dependency Declaration

**Problem**: Breaks fresh installs
**Instead**: Always update `requirements.txt`

---
### ❌ Anti-Pattern 4: Raw SQL Queries

**Problem**: Breaks abstraction, ownership, and safety guarantees.
**Instead**: Use ORM queries inside the repository layer.

```python
# BAD
db.execute("SELECT * FROM users WHERE email = :email")
```

```python
# GOOD
db.query(User).filter(User.email == email).first()
```

---

### ❌ Anti-Pattern 5: Spatial Raw SQL

```python
# BAD
db.execute(
    "SELECT * FROM locations WHERE ST_DWithin(geom, :p, :r)"
)
```

```python
# GOOD
db.query(Location).filter(
    func.ST_DWithin(Location.geom, point, radius)
)
```
---

## Changelog

| Date       | Changes         | Author |
| ---------- | --------------- | ------ |
| 2026-01-31 | Initial version | Udit   |

---

