"""
Data Models for Financial Analysis Module
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class FinancialAnalysisRequest(BaseModel):
    annual_energy_yield: float = Field(..., description="Annual energy yield in kWh")
    installed_capacity: float = Field(..., description="Installed capacity in kW")
    electricity_tariff: float = Field(..., description="Electricity tariff in currency per kWh (e.g. ₹/kWh)")
    cost_per_mw: float = Field(50000000.0, description="Cost per MW in currency")
    installation_pct: float = Field(0.10, description="Additional installation cost percentage (0-1.0)")
    annual_opex_pct: float = Field(0.02, description="Annual OPEX as fraction of CAPEX (default 0.02)")


class FinancialAnalysisResponse(BaseModel):
    annual_revenue: float = Field(..., description="Estimated annual revenue")
    estimated_project_cost: float = Field(..., description="Estimated total project cost (CAPEX)")
    annual_cost: float = Field(..., description="Estimated annual operating cost (OPEX)")
    payback_period: float = Field(..., description="Payback period in years")
    roi: float = Field(..., description="Return on Investment percentage (%)")
    currency: str = Field("INR", description="Currency symbol/code")
