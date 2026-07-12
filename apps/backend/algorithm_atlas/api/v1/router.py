from fastapi import APIRouter
from .ai import router as ai_router
from .algorithms import router as algorithms_router
from .benchmarks import router as benchmarks_router
from .experiments import router as experiments_router
from .notebook import router as notebook_router
from .problems import router as problems_router
from .progress import router as progress_router
from .simulations import router as simulations_router
from .submissions import router as submissions_router

api_router = APIRouter()
api_router.include_router(algorithms_router, prefix="/api/v1")
api_router.include_router(benchmarks_router, prefix="/api/v1")
api_router.include_router(experiments_router, prefix="/api/v1")
api_router.include_router(notebook_router, prefix="/api/v1")
api_router.include_router(ai_router, prefix="/api/v1")
api_router.include_router(simulations_router)
api_router.include_router(problems_router, prefix="/api/v1")
api_router.include_router(submissions_router, prefix="/api/v1")
api_router.include_router(progress_router, prefix="/api/v1")
