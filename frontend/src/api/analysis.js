import api from '../services/api'

/**
 * Centralized Analysis API Module (Task 2 API Layer)
 * Connects frontend analysis workflow to FastAPI backend endpoints.
 */
export const analysisAPI = {
  /**
   * POST /analysis/run — Runs complete end-to-end unified analysis pipeline for given coordinates.
   * @param {Object} data - { latitude, longitude, target_capacity, preferred_deployment_type, constraints }
   */
  runUnifiedAnalysis: (data) => api.post('/analysis/run', data),

  /**
   * POST /pipeline/run — Runs full multi-stage deployment pipeline.
   * @param {Object} data - { latitude, longitude, site_id, target_capacity, preferred_deployment_type, constraints }
   */
  runPipeline: (data) => api.post('/pipeline/run', data),

  /**
   * GET /assessment — Query resource assessment & candidate site ranking for lat/lon.
   * @param {number} latitude
   * @param {number} longitude
   */
  getAssessment: (latitude, longitude) =>
    api.get('/assessment', { params: { latitude, longitude } }),

  /**
   * POST /assessment/energy-estimate — Calculate annual energy yield.
   * @param {Object} data
   */
  estimateEnergy: (data) => api.post('/assessment/energy-estimate', data),
}

export default analysisAPI
