import unittest

class TestCleanUserWorkspace(unittest.TestCase):

    def test_workspace_v2_template_clean_elements(self):
        filepath = r'C:\OsintNeoAi\templates\workspace_v2.html'
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<title>OSINT NEO AI — User Intelligence Workspace</title>', content)
        self.assertIn('elements: []', content)

    def test_public_workspace_v2_clean_elements(self):
        filepath = r'C:\OsintNeoAi\public\workspace_v2.html'
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<title>OSINT NEO AI — User Intelligence Workspace</title>', content)
        self.assertIn('elements: []', content)

    def test_public_workspace_clean_title(self):
        filepath = r'C:\OsintNeoAi\public\workspace.html'
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<title>OSINT NEO AI — User Intelligence Workspace</title>', content)
        self.assertIn('No nodes extracted.', content)

if __name__ == '__main__':
    unittest.main()
