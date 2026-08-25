import os
import tempfile
import unittest

from backend.app.main import analyze_site, authenticate_user, create_project, generate_report, register_user


class ExtendedFeatureTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test.sqlite3')
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_and_login_flow(self):
        user = register_user('analyst@example.com', 'strong-pass', 'Analyst')
        self.assertEqual(user.email, 'analyst@example.com')
        token = authenticate_user('analyst@example.com', 'strong-pass')
        self.assertTrue(token)

    def test_create_project_and_generate_report(self):
        register_user('analyst@example.com', 'strong-pass', 'Analyst')
        project = create_project('analyst@example.com', 'Demo Project', 'Prototype')
        self.assertEqual(project.name, 'Demo Project')

        report = generate_report(project.id, 'Demo Project', analyze_site())
        self.assertTrue(report.file_path.endswith('.pdf'))
        self.assertTrue(os.path.exists(report.file_path))
        self.assertTrue(report.file_path.endswith('.pdf'))


if __name__ == '__main__':
    unittest.main()
