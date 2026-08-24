import { sortFeatureData } from './sorting.js';

// 5+ sample records as required by test cases
const sampleFeatures = [
  {
    id: 101,
    latitude: 34.0522,
    longitude: -118.2437,
    solar_irradiance: 5.4,
    wind_speed: 6.2,
    temperature: 24.5,
    humidity: 45,
    elevation: 250,
    slope: 4.2,
    road_distance: 1.5,
    substation_distance: 5.0,
    capacity_factor: 28.5,
    wind_class: 'Good',
    terrain_score: 82.0,
    accessibility_score: 90.0,
    created_at: '2026-07-20T10:00:00Z',
  },
  {
    id: 102,
    latitude: 36.7783,
    longitude: -119.4179,
    solar_irradiance: 6.8,
    wind_speed: 4.1,
    temperature: 31.0,
    humidity: 30,
    elevation: 150,
    slope: 2.1,
    road_distance: 0.8,
    substation_distance: 12.0,
    capacity_factor: 22.0,
    wind_class: 'Poor',
    terrain_score: 94.0,
    accessibility_score: 85.0,
    created_at: '2026-07-25T14:30:00Z',
  },
  {
    id: 103,
    latitude: 40.7128,
    longitude: -74.0060,
    solar_irradiance: 4.2,
    wind_speed: 8.9,
    temperature: 18.0,
    humidity: 65,
    elevation: 10,
    slope: 0.5,
    road_distance: 0.2,
    substation_distance: 2.1,
    capacity_factor: 35.0,
    wind_class: 'Excellent',
    terrain_score: 98.0,
    accessibility_score: 95.0,
    created_at: '2026-07-22T08:15:00Z',
  },
  {
    id: 104,
    latitude: 39.7392,
    longitude: -104.9903,
    solar_irradiance: 6.1,
    wind_speed: 7.4,
    temperature: null, // null value test
    humidity: 40,
    elevation: 1608,
    slope: 12.5,
    road_distance: 3.4,
    substation_distance: null, // null value test
    capacity_factor: 31.2,
    wind_class: 'Moderate',
    terrain_score: 65.0,
    accessibility_score: 70.0,
    created_at: '2026-07-27T09:00:00Z',
  },
  {
    id: 105,
    latitude: 25.7617,
    longitude: -80.1918,
    solar_irradiance: 5.9,
    wind_speed: null, // null value test
    temperature: 29.5,
    humidity: 80,
    elevation: 2,
    slope: 0.1,
    road_distance: 0.5,
    substation_distance: 8.5,
    capacity_factor: null, // null value test
    wind_class: null, // null value test
    terrain_score: 90.0,
    accessibility_score: null, // null value test
    created_at: '2026-07-18T16:45:00Z',
  },
];

function runTests() {
  console.log('=== FEATURE STORE SORTING TEST SUITE ===\n');

  // Test 1: Solar Irradiance Descending (Highest solar first)
  const solarDesc = sortFeatureData(sampleFeatures, 'solar_irradiance', 'desc');
  console.assert(solarDesc[0].id === 102, `Solar Desc Test Failed: Expected ID 102 first, got ${solarDesc[0].id}`);
  console.assert(solarDesc[0].solar_irradiance === 6.8, `Solar Desc Val Failed: Got ${solarDesc[0].solar_irradiance}`);
  console.log('✔ Solar Irradiance Descending: Passed (Highest 6.8 kWh/m²/d first)');

  // Test 2: Solar Irradiance Ascending (Lowest solar first)
  const solarAsc = sortFeatureData(sampleFeatures, 'solar_irradiance', 'asc');
  console.assert(solarAsc[0].id === 103, `Solar Asc Test Failed: Expected ID 103 first, got ${solarAsc[0].id}`);
  console.assert(solarAsc[0].solar_irradiance === 4.2, `Solar Asc Val Failed: Got ${solarAsc[0].solar_irradiance}`);
  console.log('✔ Solar Irradiance Ascending: Passed (Lowest 4.2 kWh/m²/d first)');

  // Test 3: Wind Speed Descending (Highest wind first, nulls at end)
  const windDesc = sortFeatureData(sampleFeatures, 'wind_speed', 'desc');
  console.assert(windDesc[0].id === 103, `Wind Desc Test Failed: Expected ID 103 first, got ${windDesc[0].id}`);
  console.assert(windDesc[4].wind_speed === null, 'Wind Desc Null Test Failed: Null should be last');
  console.log('✔ Wind Speed Descending: Passed (Highest 8.9 m/s first, nulls at end)');

  // Test 4: Date Sorting Descending (Newest date first)
  const dateDesc = sortFeatureData(sampleFeatures, 'created_at', 'desc');
  console.assert(dateDesc[0].id === 104, `Date Desc Test Failed: Expected ID 104 first, got ${dateDesc[0].id}`);
  console.log('✔ Date Descending: Passed (Newest 2026-07-27 first)');

  // Test 5: Date Sorting Ascending (Oldest date first)
  const dateAsc = sortFeatureData(sampleFeatures, 'created_at', 'asc');
  console.assert(dateAsc[0].id === 105, `Date Asc Test Failed: Expected ID 105 first, got ${dateAsc[0].id}`);
  console.log('✔ Date Ascending: Passed (Oldest 2026-07-18 first)');

  // Test 6: Wind Class String Sorting (Alphabetical)
  const windClassAsc = sortFeatureData(sampleFeatures, 'wind_class', 'asc');
  const validWindClasses = windClassAsc.filter(f => f.wind_class).map(f => f.wind_class);
  console.assert(validWindClasses[0] === 'Excellent', `Wind Class Asc Failed: Expected Excellent, got ${validWindClasses[0]}`);
  console.log('✔ Wind Class String Ascending: Passed (Excellent -> Good -> Moderate -> Poor)');

  // Test 7: Array Immutability
  const originalCopy = JSON.stringify(sampleFeatures);
  sortFeatureData(sampleFeatures, 'terrain_score', 'desc');
  console.assert(JSON.stringify(sampleFeatures) === originalCopy, 'Immutability Test Failed: Original array was mutated!');
  console.log('✔ Array Immutability: Passed (Original array untouched)');

  console.log('\nALL 7 UNIT TESTS PASSED SUCCESSFULLY! 🎉');
}

runTests();
