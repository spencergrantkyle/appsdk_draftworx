"""Unified MCP server hosting both Pizzaz and Solar System widgets.

This server combines both MCP servers and serves static assets from Railway.
It exposes separate endpoints for each widget collection while sharing the assets.
"""

import os
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Get the base directory
BASE_DIR = Path(__file__).parent

# Import both MCP servers
app = FastAPI(title="Unified MCP Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Mount static assets
assets_dir = BASE_DIR / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
else:
    # Fallback if assets don't exist yet
    print(f"Warning: Assets directory not found at {assets_dir}")


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring."""
    return {
        "status": "healthy",
        "services": [
            "pizzaz-mcp",
            "solar-system-mcp",
            "static-assets"
        ],
        "endpoints": {
            "pizzaz": "/pizzaz/mcp",
            "solar": "/solar/mcp",
            "health": "/health",
            "assets": "/assets/"
        }
    }


# Create middleware to pass through requests to sub-applications
class SubAppMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, sub_app, prefix: str):
        super().__init__(app)
        self.sub_app = sub_app
        self.prefix = prefix

    async def dispatch(self, request: StarletteRequest, call_next):
        if request.url.path.startswith(self.prefix):
            # Strip prefix for sub-application
            path_info = request.url.path[len(self.prefix):]
            scope = request.scope
            scope["path"] = path_info
            # Create new request with updated path
            return await self.sub_app(scope, request.receive, request._send)


# Import and create sub-applications
import pizzaz_server_python.main as pizzaz_module
import solar_system_server_python.main as solar_module

pizzaz_app = pizzaz_module.app
solar_app = solar_module.app

# Mount sub-applications directly
app.mount("/pizzaz", pizzaz_app)
app.mount("/solar", solar_app)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Unified MCP Server",
        "endpoints": {
            "pizzaz_mcp": "/pizzaz/mcp",
            "solar_mcp": "/solar/mcp",
            "health": "/health",
            "assets": "/assets/",
            "pizzaz_tools": [
                "pizza-map",
                "pizza-carousel",
                "pizza-albums",
                "pizza-list",
                "pizza-video"
            ],
            "solar_tools": [
                "focus-solar-planet"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("unified_server:app", host="0.0.0.0", port=port)
