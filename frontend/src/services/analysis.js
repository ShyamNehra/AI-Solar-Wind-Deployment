const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function runSiteAnalysis(payload) {
  const response = await fetch(`${API_BASE_URL}/api/analysis`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errMsg = "An error occurred during analysis.";
    try {
      const errData = await response.json();
      errMsg = errData.detail || errMsg;
    } catch (e) {
      // JSON parsing failed
    }
    throw new Error(errMsg);
  }

  return await response.json();
}
