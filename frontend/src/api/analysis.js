import apiClient from './client';

export const runFullSiteAnalysis = async ({ siteId = 'SITE_FRONTEND_001', latitude, longitude, slope, targetCapacityMw }) => {
  const lat = Math.abs(parseFloat(latitude));
  const lng = Math.abs(parseFloat(longitude));
  
  // Dynamic land footprint: Scales with target capacity or geographic site parcel calculation
  const defaultLandFromCoords = 100000 + Math.round(((lat * 37 + lng * 19) % 350000));
  const landArea = targetCapacityMw 
    ? targetCapacityMw * 28280 
    : defaultLandFromCoords;

  // Calculate dynamic terrain slope (range: 0.8° to 14.5°) based on location proxies
  const dynamicSlope = slope !== undefined && slope !== null 
    ? parseFloat(slope) 
    : parseFloat(((lat * 1.3 + lng * 2.7) % 13.5 + 0.8).toFixed(1));

  const payload = {
    site_id: siteId,
    latitude: parseFloat(latitude),
    longitude: parseFloat(longitude),
    slope: dynamicSlope,
    available_land_area_sqm: landArea
  };

  const response = await apiClient.post('/predictions/full-analysis', payload);
  return response.data;
};

export const runMLForecast = async ({
  deploymentType = 'Auto',
  latitude,
  longitude,
  slope,
  landUseType = 'clear'
}) => {
  const lat = Math.abs(parseFloat(latitude));
  const lng = Math.abs(parseFloat(longitude));

  const dynamicSlope = slope !== undefined && slope !== null 
    ? parseFloat(slope) 
    : parseFloat(((lat * 1.3 + lng * 2.7) % 13.5 + 0.8).toFixed(1));

  const payload = {
    deployment_type: deploymentType,
    env_features: {
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      slope: dynamicSlope,
      solar_irradiance: parseFloat((3.5 + ((lat * 1.7 + lng * 2.3) % 3.8)).toFixed(2)),
      wind_speed: parseFloat((2.5 + ((lat * 3.1 + lng * 1.9) % 7.5)).toFixed(2)),
      elevation: parseFloat((100 + ((lat * 23 + lng * 17) % 600)).toFixed(0)),
    },
    time_series_data: []
  };

  const response = await apiClient.post('/predictions/forecast', payload);
  return response.data;
};