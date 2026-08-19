/**
 * @file exportService.js
 * @description Client Export Utility - Provides client-side document processing,
 * UTF-8 BOM CSV generation, JSON assessment dumping, and print/PDF export triggers.
 */

export function triggerBrowserPrint() {
  window.print();
}

export function generateCsvBlob(csvContent) {
  const bom = '\uFEFF';
  return new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' });
}

export function downloadBlob(blob, filename) {
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
