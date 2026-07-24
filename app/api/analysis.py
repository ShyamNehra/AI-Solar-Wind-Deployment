from fastapi import APIRouter, Depends, HTTPException, status
from schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_pipeline import AnalysisPipelineService

router = APIRouter(prefix="/analysis", tags=["Analysis"])

def get_analysis_pipeline() -> AnalysisPipelineService:
    """
    Dependency injection provider for the AnalysisPipelineService.
    """
    return AnalysisPipelineService()

@router.post(
    "",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Run site suitability analysis",
    description="Executes the complete site analysis pipeline. Retrieves solar and wind parameters, scores the site, and recommends deployment technology in a consolidated object."
)
def run_site_analysis(
    request: AnalysisRequest,
    pipeline: AnalysisPipelineService = Depends(get_analysis_pipeline)
):
    """
    Run site analysis endpoint.
    """
    try:
        return pipeline.run_analysis(request)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except (ConnectionError, TimeoutError) as ce:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Network error connecting to external data source: {str(ce)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch data or process analysis: {str(e)}"
        )
