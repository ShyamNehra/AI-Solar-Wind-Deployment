import unittest

from backend.app.main import analyze_site


class SiteAnalysisTests(unittest.TestCase):
    def test_analyze_site_returns_expected_summary(self):
        summary = analyze_site()

        self.assertEqual(summary['site']['name'], 'Bangalore, India')
        self.assertIn('metrics', summary)
        self.assertIn('insights', summary)
        self.assertIn('data_sources', summary)
        self.assertGreaterEqual(summary['metrics']['solar_score'], 0)
        self.assertLessEqual(summary['metrics']['solar_score'], 100)
        self.assertGreaterEqual(summary['metrics']['wind_score'], 0)
        self.assertLessEqual(summary['metrics']['wind_score'], 100)
        self.assertGreaterEqual(summary['metrics']['infrastructure_score'], 0)
        self.assertLessEqual(summary['metrics']['infrastructure_score'], 100)
        self.assertGreaterEqual(summary['metrics']['overall_suitability_score'], 0)
        self.assertLessEqual(summary['metrics']['overall_suitability_score'], 100)
        self.assertTrue(summary['insights'])


if __name__ == '__main__':
    unittest.main()
