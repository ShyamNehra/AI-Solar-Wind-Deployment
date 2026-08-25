"""
Integration Tests for Updated Pipeline & API Endpoints
"""

import pytest
from app.services.workflow_pipeline_service import WorkflowPipelineService


def test_workflow_pipeline_execution():
    """Verify run_pipeline produces prediction, feasibility, energy yield, and financial outputs."""
    pipeline_service = WorkflowPipelineService()
    res = pipeline_service.run_pipeline(
        latitude=26.9124,
        longitude=75.7873,
        target_capacity=1000.0,
        preferred_deployment_type="Hybrid"
    )

    assert "deployment" in res
    assert "technical_feasibility" in res
    assert "feasibility_score" in res
    assert "annual_energy_yield" in res
    assert "annual_revenue" in res
    assert "estimated_project_cost" in res
    assert "payback_period" in res
    assert "roi" in res

    assert res["annual_energy_yield"] > 0
    assert res["annual_revenue"] > 0
    assert res["estimated_project_cost"] > 0
    assert res["payback_period"] > 0
    assert res["roi"] > 0
