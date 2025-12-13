---
title: FastAPI App.py Refactoring Plan - Modular Architecture
type: note
permalink: development/fast-api-app-py-refactoring-plan-modular-architecture
---

# FastAPI App.py Refactoring Plan

## Problem Summary
Current `app.py` file is oversized at **1,160 lines, 40KB** and violates Single Responsibility Principle. It contains:
- Multiple classes (AnalysisResponse, R2StorageClient, NoOpLimiter)
- Large functions (analyze_video ~300+ lines)
- Mixed concerns: app setup, business logic, data models, utilities
- Poor testability due to monolithic structure

## Target Architecture: Modular Monolith

### New Directory Structure
```
backend/src/kinemotion_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI creation, middleware, global config
│   ├── config.py            # Settings, environment variables
│   ├── dependencies.py      # FastAPI dependencies (auth, db, etc.)
│   ├── exceptions.py        # Custom exceptions
│   └── middleware.py        # Custom middleware (already exists)
├── models/
│   ├── __init__.py
│   ├── analysis.py          # AnalysisResponse (extract from app.py)
│   ├── storage.py           # R2StorageClient (extract from app.py)
│   └── feedback.py          # Feedback models (already exists)
├── routes/
│   ├── __init__.py
│   ├── analysis.py          # Video analysis routes (main functionality)
│   ├── health.py            # Health check routes
│   ├── platform.py          # Platform info routes
│   └── feedback.py          # Feedback routes (already exists)
├── services/
│   ├── __init__.py
│   ├── video_processor.py   # _process_video_async logic
│   ├── storage_service.py   # R2 operations
│   ├── analysis_service.py  # Analysis orchestration
│   └── validation.py        # Input validation functions
└── utils/
    ├── __init__.py
    └── helpers.py           # General utility functions
```

## Implementation Plan

### Phase 1: Preparation (Day 1)
1. **Backup Current State**
   ```bash
   cp app.py app.py.backup
   git add app.py.backup
   git commit -m "backup: Save current app.py before refactoring"
   ```

2. **Create Directory Structure**
   ```bash
   mkdir -p app models routes services utils
   touch app/__init__.py models/__init__.py routes/__init__.py
   touch services/__init__.py utils/__init__.py
   ```

3. **Setup Basic Package Structure**
   - Create `__init__.py` files for proper Python packages
   - Ensure proper relative imports work

### Phase 2: Extract Models (Day 1-2)
1. **Move AnalysisResponse** to `models/analysis.py`
   ```python
   from pydantic import BaseModel, Field
   from typing import Any, Optional
   from uuid import UUID

   class AnalysisResponse(BaseModel):
       status_code: int
       message: str
       metrics: Optional[dict[str, Any]] = None
       results_url: Optional[str] = None
       debug_video_url: Optional[str] = None
       original_video_url: Optional[str] = None
       processing_time_s: Optional[float] = None
       error: Optional[str] = None
       # ... rest of the class
   ```

2. **Move R2StorageClient** to `models/storage.py`
   ```python
   import boto3
   from botocore.exceptions import ClientError
   import structlog

   class R2StorageClient:
       def __init__(self) -> None:
           # ... implementation
   ```

3. **Update Imports** in `app.py` and other files

### Phase 3: Create Service Layer (Day 2-3)
1. **Extract Video Processing** to `services/video_processor.py`
   ```python
   async def process_video_async(
       video_path: str,
       jump_type: str,
       quality: str,
       output_video: str | None = None,
       timer: PerformanceTimer | None = None,
       pose_tracker: PoseTracker | None = None,
   ) -> dict[str, Any]:
       # Extract from app.py
   ```

2. **Create Storage Service** `services/storage_service.py`
   ```python
   class StorageService:
       def __init__(self):
           self.client = R2StorageClient()

       async def upload_video(self, local_path: str, remote_key: str) -> str:
           # Storage logic
   ```

3. **Extract Validation** to `services/validation.py`
   ```python
   def validate_video_file(file: UploadFile) -> None:
       # Extract _validate_video_file from app.py
   ```

### Phase 4: Modularize Routes (Day 3-4)
1. **Create Analysis Routes** `routes/analysis.py`
   ```python
   from fastapi import APIRouter, Depends, File, Form, Header
   from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

   router = APIRouter(prefix="/api", tags=["Analysis"])

   @router.post("/analyze")
   async def analyze_video(
       # Implementation from app.py
   ):
   ```

2. **Create Health Routes** `routes/health.py`
   ```python
   router = APIRouter(tags=["Health"])

   @router.get("/health")
   async def health_check() -> dict[str, Any]:
       # Health check implementation
   ```

3. **Create Platform Routes** `routes/platform.py`
   ```python
   router = APIRouter(prefix="/api", tags=["Platform"])

   @router.get("/platform")
   async def get_platform_info() -> dict[str, Any]:
       # Platform info implementation
   ```

### Phase 5: Update Main Application (Day 4)
1. **Simplify main.py**
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   # Import routers
   from .routes import analysis, health, platform
   from .routes.feedback import router as feedback_router

   # Create app
   app = FastAPI(
       title="Kinemotion Backend API",
       description="Video-based kinematic analysis API for athletic performance",
       version="0.1.0",
       lifespan=lifespan,
   )

   # Include routers
   app.include_router(analysis.router)
   app.include_router(health.router)
   app.include_router(platform.router)
   app.include_router(feedback_router)

   # CORS and middleware setup
   # ... existing middleware configuration
   ```

2. **Create config.py**
   ```python
   import os
   from typing import List

   class Settings:
       CORS_ORIGINS: List[str] = [...]
       R2_ENDPOINT_URL: str = os.getenv("R2_ENDPOINT_URL", "")
       # ... other settings

   settings = Settings()
   ```

3. **Create dependencies.py**
   ```python
   from fastapi import Depends
   from .auth import SupabaseAuth

   auth = SupabaseAuth()

   async def get_current_user_id(
       credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
   ) -> str:
       return auth.get_user_id(credentials.credentials)
   ```

### Phase 6: Testing & Validation (Day 5)
1. **Run Existing Tests**
   ```bash
   uv run pytest
   uv run pyright
   ```

2. **Test New Structure**
   ```bash
   # Test imports work
   python -c "from backend.src.kinemotion_backend.app.main import app; print('✓ App imports successfully')"

   # Test routes
   python -c "from backend.src.kinemotion_backend.routes.analysis import router; print('✓ Analysis routes import successfully')"
   ```

3. **Integration Testing**
   ```bash
   # Start server
   uvicorn backend.src.kinemotion_backend.app.main:app --reload

   # Test endpoints
   curl http://localhost:8000/health
   ```

## Migration Strategy

### Safe Migration Approach
1. **Parallel Development**: Keep app.py until new structure is fully tested
2. **Incremental Changes**: Implement one module at a time
3. **Feature Flags**: Use environment variables to switch between old/new if needed
4. **Comprehensive Testing**: Test each phase thoroughly before proceeding

### Rollback Plan
- Keep `app.py.backup` as safety net
- Use git branches for each phase
- Test thoroughly before merging
- Have quick rollback procedure documented

## Benefits of Refactoring

### Maintainability
- **Single Responsibility**: Each file has one clear purpose
- **Easier Debugging**: Issues isolated to specific modules
- **Code Navigation**: Logical organization makes finding code easier

### Testability
- **Unit Testing**: Smaller, focused functions are easier to test
- **Mocking Services**: Services can be easily mocked for testing
- **Isolation**: Test failures point to specific modules

### Reusability
- **Service Components**: Can be reused across different endpoints
- **Utility Functions**: Shared across multiple modules
- **Database Operations**: Centralized in service layer

### Team Collaboration
- **Parallel Development**: Different team members can work on different modules
- **Clear Ownership**: Each module has clear responsibility boundaries
- **Reduced Conflicts**: Less likely to have merge conflicts

### Scalability
- **Feature Addition**: New features can be added as new modules
- **Performance Optimization**: Individual modules can be optimized independently
- **Technology Migration**: Easier to replace individual components

## Risk Mitigation

### Technical Risks
1. **Import Issues**: Test imports thoroughly after each move
2. **Circular Dependencies**: Use dependency injection to avoid
3. **Performance**: Monitor performance during transition
4. **Breaking Changes**: Maintain API compatibility

### Process Risks
1. **Time Overrun**: Each phase has clear time estimates
2. **Team Coordination**: Clear documentation for all team members
3. **Knowledge Transfer**: Comprehensive documentation of new structure
4. **Rollback**: Quick rollback procedures if issues arise

## Post-Refactoring Improvements

### Immediate Benefits (Day 5+)
- Easier to add new features
- Better code organization
- Improved testability
- Reduced merge conflicts

### Long-term Benefits (Month 1+)
- Easier onboarding for new team members
- Better performance optimization opportunities
- Potential for microservices migration if needed
- Improved code maintainability and scalability

## Success Criteria
- [ ] All existing tests pass
- [ ] No breaking changes to API
- [ ] Code is more modular and organized
- [ ] Team can work efficiently on different modules
- [ ] Performance remains stable or improves
- [ ] Documentation is comprehensive and up-to-date

This refactoring will transform the monolithic 1,160-line app.py into a maintainable, modular architecture that follows FastAPI best practices while ensuring no disruption to existing functionality.

### Phase 1: Preparation (Day 1)
1. **Backup Current State**
   ```bash
   cp app.py app.py.backup
   git add app.py.backup
   git commit -m "backup: Save current app.py before refactoring"
   ```
### Phase 1: Preparation (Day 1)
1. **Backup Current State with Git**
   ```bash
   # Create dedicated branch for refactoring
   git checkout -b refactor/fastapi-modular-architecture
   git add -A
   git commit -m "feat: start FastAPI modular architecture refactoring

   - Current app.py: 1,160 lines, monolithic structure
   - Target: Modular architecture with clear separation of concerns
   - All existing tests must continue to pass
   "
   ```

### Rollback Plan
- Keep `app.py.backup` as safety net
- Use git branches for each phase
- Test thoroughly before merging
- Have quick rollback procedure documented
### Rollback Plan
- Use git for version control and rollback safety
- Commit after each phase for granular rollback points
- Test thoroughly before merging to main
- Quick rollback procedures:
  ```bash
  # Rollback to specific phase
  git revert <phase-commit-hash>

  # Or reset to previous state (discarding changes)
  git reset --hard <commit-hash>
  ```
