import api from './api';

export async function exportReport(
  siteId: number,
  format: 'pdf' | 'excel',
  reportType: 'site_assessment' | 'potential' | 'feasibility'
): Promise<Blob> {
  const response = await api.post(
    `/sites/${siteId}/reports/export?format=${format}&report_type=${reportType}`,
    null,
    {
      responseType: 'blob',
    }
  );
  return response.data;
}

export function triggerDownload(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.parentNode?.removeChild(link);
  window.URL.revokeObjectURL(url);
}
