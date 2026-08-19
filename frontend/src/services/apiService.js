/**
 * @file apiService.js
 * @description Service Facade - Centralizes, unifies, and re-exports REST API endpoints
 * and Axios networking client handlers from src/api/ (analysis.js, sites.js, auth.js, client.js).
 */

import apiClient from '../api/client';
import { runFullSiteAnalysis, executeMlForecast } from '../api/analysis';
import { fetchSavedSites, saveSite, deleteSavedSite } from '../api/sites';
import { loginUser, registerUser, fetchMe } from '../api/auth';

export {
  apiClient,
  runFullSiteAnalysis,
  executeMlForecast,
  fetchSavedSites,
  saveSite,
  deleteSavedSite,
  loginUser,
  registerUser,
  fetchMe
};
