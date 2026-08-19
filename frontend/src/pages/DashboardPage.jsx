/**
 * @file DashboardPage.jsx
 * @description Page View Wrapper - Encapsulates the core site assessment interface,
 * interactive map canvas, and evaluation dashboard from src/components/SiteAnalysisScreen.jsx.
 * Conforms to top-level route view architecture.
 */

import React from 'react';
import SiteAnalysisScreen from '../components/SiteAnalysisScreen';

export default function DashboardPage() {
  return <SiteAnalysisScreen />;
}
