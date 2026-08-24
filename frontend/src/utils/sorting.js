/**
 * Reusable sorting utility for Feature Store and spatial dataset tables.
 * 
 * Supports:
 * - 16 fields: ID, Latitude, Longitude, Solar Irradiance, Wind Speed, Temperature,
 *   Humidity, Elevation, Slope, Road Distance, Substation Distance, Capacity Factor,
 *   Wind Class, Terrain Score, Accessibility, Date.
 * - Ascending ('asc') and Descending ('desc') order.
 * - Field types: numbers, strings, dates, null, and undefined values.
 * - Pure function: Never mutates the original array; returns a new sorted copy.
 */

/**
 * Maps field key aliases to normalized property names on feature records.
 */
function getFieldValue(item, field) {
  if (!item) return null;

  switch (field) {
    case 'date':
    case 'created_at':
      return item.created_at || item.date || null;
    case 'accessibility':
    case 'accessibility_score':
      return item.accessibility_score ?? item.accessibility ?? null;
    default:
      return item[field] ?? null;
  }
}

/**
 * Checks if a value is null, undefined, or empty string.
 */
function isNil(val) {
  return val === null || val === undefined || val === '';
}

/**
 * Sorts an array of feature objects by a specified field and order.
 * 
 * @param {Array} data - Array of feature records to sort.
 * @param {string} sortField - The field name to sort by.
 * @param {string} sortOrder - 'asc' or 'desc' (default: 'asc').
 * @returns {Array} A new array containing the sorted items.
 */
export function sortFeatureData(data, sortField = 'id', sortOrder = 'asc') {
  if (!Array.isArray(data)) return [];
  if (data.length <= 1) return [...data];

  const isAsc = sortOrder.toLowerCase() === 'asc';

  return [...data].sort((a, b) => {
    const valA = getFieldValue(a, sortField);
    const valB = getFieldValue(b, sortField);

    const nilA = isNil(valA);
    const nilB = isNil(valB);

    // If both values are null/undefined, keep original relative order
    if (nilA && nilB) return 0;

    // Place null/undefined values at the end of the table regardless of sort order
    if (nilA) return 1;
    if (nilB) return -1;

    let comparison = 0;

    // 1. Date comparison
    if (sortField === 'created_at' || sortField === 'date' || valA instanceof Date || valB instanceof Date) {
      const timeA = new Date(valA).getTime();
      const timeB = new Date(valB).getTime();
      
      if (!isNaN(timeA) && !isNaN(timeB)) {
        comparison = timeA - timeB;
      } else {
        comparison = String(valA).localeCompare(String(valB));
      }
    }
    // 2. Numeric comparison
    else if (typeof valA === 'number' && typeof valB === 'number') {
      comparison = valA - valB;
    }
    // 3. Convert numeric strings to numbers if both are numeric
    else if (!isNaN(valA) && !isNaN(valB) && typeof valA !== 'boolean' && typeof valB !== 'boolean') {
      comparison = Number(valA) - Number(valB);
    }
    // 4. String comparison (case-insensitive, numeric-aware)
    else {
      const strA = String(valA);
      const strB = String(valB);
      comparison = strA.localeCompare(strB, undefined, { numeric: true, sensitivity: 'base' });
    }

    return isAsc ? comparison : -comparison;
  });
}

export default sortFeatureData;
