# Module Responsibility Mapping

## Overview

This document defines the responsibilities of each module in the Renewable Energy Site Suitability Prediction System. Each module has a dedicated role to ensure modularity, scalability, and maintainability.

---

# 1. Authentication Module

## Responsibilities
- User registration
- User login/logout
- Password encryption and validation
- Session management
- User authorization (Admin/User roles)

## Inputs
- Email
- Password

## Outputs
- Authentication token
- User session

---

# 2. Solar Prediction Module

## Responsibilities
- Process solar-related environmental data
- Predict solar energy generation
- Calculate solar efficiency
- Store prediction results

## Inputs
- Solar radiation
- Temperature
- Humidity

## Outputs
- Predicted solar power
- Solar efficiency score

---

# 3. Wind Prediction Module

## Responsibilities
- Analyze wind-related environmental data
- Predict wind energy generation
- Calculate wind potential
- Store prediction results

## Inputs
- Wind speed
- Air pressure
- Temperature

## Outputs
- Predicted wind power
- Wind efficiency score

---

# 4. Site Suitability Module

## Responsibilities
- Combine solar and wind prediction results
- Calculate overall suitability score
- Rank locations
- Recommend the most suitable renewable energy source

## Inputs
- Solar prediction
- Wind prediction
- Environmental data

## Outputs
- Suitability score
- Site ranking
- Recommendation

---

# 5. Database Module

## Responsibilities
- Store user information
- Store project details
- Store environmental datasets
- Store prediction results
- Manage reports
- Perform CRUD operations

## Tables Managed
- Users
- Projects
- Sites
- EnvironmentalData
- SolarPrediction
- WindPrediction
- SuitabilityScore
- Reports

---

# 6. Reports Module

## Responsibilities
- Generate prediction reports
- Export reports (PDF/CSV)
- Summarize analysis results
- Store generated reports

## Outputs
- PDF reports
- CSV reports
- Downloadable summaries

---

# 7. Dashboard Module

## Responsibilities
- Display project overview
- Show prediction results
- Visualize charts and graphs
- Display site rankings
- Show recent reports

## Features
- Interactive dashboard
- Data visualization
- Performance metrics

---

# 8. API Services Module

## Responsibilities
- Handle frontend-backend communication
- Receive client requests
- Validate input data
- Fetch environmental data
- Return prediction results
- Integrate external APIs (e.g., NASA POWER)

## Endpoints
- Authentication APIs
- Prediction APIs
- Report APIs
- Dashboard APIs

---

# Module Interaction Flow

Authentication
        ↓
Dashboard
        ↓
API Services
        ↓
Database
        ↓
Environmental Data
        ↓
Solar Prediction
        ↓
Wind Prediction
        ↓
Site Suitability
        ↓
Reports
        ↓
Dashboard