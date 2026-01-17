"""
LLM Providers API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import logging

from app.database import get_db
from app.models.llm_provider import LLMProvider
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_providers(db: AsyncSession = Depends(get_db)):
    """List all configured LLM providers"""

    # Get from service (runtime configuration)
    runtime_providers = llm_service.list_providers()

    # Get from database (historical data)
    result = await db.execute(select(LLMProvider))
    db_providers = result.scalars().all()

    # Merge data
    providers_map = {p["name"]: p for p in runtime_providers}

    response = []
    for db_provider in db_providers:
        provider_info = providers_map.get(db_provider.name, {})
        response.append({
            "id": db_provider.id,
            "name": db_provider.name,
            "type": db_provider.type,
            "enabled": db_provider.enabled,
            "model": provider_info.get("model", "unknown"),
            "total_requests": db_provider.total_requests,
            "total_tokens": db_provider.total_tokens,
            "total_cost": db_provider.total_cost,
            "success_rate": db_provider.success_rate,
            "avg_response_time": db_provider.avg_response_time,
            "status": db_provider.status
        })

    # Add runtime providers not in database
    for name, provider in providers_map.items():
        if not any(p["name"] == name for p in response):
            response.append({
                "id": None,
                "name": name,
                "type": provider["provider"],
                "enabled": True,
                "model": provider["model"],
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "success_rate": 0.0,
                "avg_response_time": 0.0,
                "status": "active"
            })

    return response


@router.get("/{provider_name}/test")
async def test_provider(provider_name: str):
    """Test a provider with a simple query"""

    try:
        result = await llm_service.generate(
            prompt="Say 'Hello, I am working correctly!' in a friendly way.",
            provider=provider_name
        )

        return {
            "status": "success",
            "provider": result["provider"],
            "model": result["model"],
            "response": result["response"],
            "duration": result["duration"],
            "tokens_used": result.get("tokens_used"),
            "cost": result.get("cost")
        }

    except Exception as e:
        logger.error(f"Provider test failed for {provider_name}: {e}")
        return {
            "status": "error",
            "provider": provider_name,
            "error": str(e)
        }


@router.get("/{provider_name}/models")
async def get_provider_models(provider_name: str):
    """Get available models for a provider"""

    # This is a simplified version
    # In production, this would query the actual provider APIs

    models = {
        "ollama": [
            "qwen2.5:7b",
            "llama3",
            "mistral",
            "codellama",
            "phi"
        ],
        "gemini": [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ],
        "claude": [
            "claude-sonnet-4.5",
            "claude-opus-4",
            "claude-haiku-4"
        ]
    }

    if provider_name not in models:
        raise HTTPException(status_code=404, detail="Provider not found")

    return {
        "provider": provider_name,
        "models": models[provider_name]
    }


@router.get("/stats")
async def get_provider_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregate statistics for all providers"""

    result = await db.execute(select(LLMProvider))
    providers = result.scalars().all()

    total_requests = sum(p.total_requests for p in providers)
    total_tokens = sum(p.total_tokens for p in providers)
    total_cost = sum(p.total_cost for p in providers)

    return {
        "total_providers": len(providers),
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "providers": [
            {
                "name": p.name,
                "type": p.type,
                "requests": p.total_requests,
                "tokens": p.total_tokens,
                "cost": p.total_cost,
                "success_rate": p.success_rate,
                "avg_response_time": p.avg_response_time
            }
            for p in providers
        ]
    }
