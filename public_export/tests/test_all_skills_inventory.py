import unittest
import os
import glob

class TestAllSkillsInventory(unittest.TestCase):

    def setUp(self):
        self.skills_dir_v1 = r"C:\Amd949609_Antigravity_v1\skills"
        self.skills_dir_repo = r"C:\OsintNeoAi\.agents\skills"

    def test_v1_skills_directory_exists_and_populated(self):
        self.assertTrue(os.path.exists(self.skills_dir_v1), "Skills directory must exist in unified profile")
        skill_folders = [d for d in os.listdir(self.skills_dir_v1) if os.path.isdir(os.path.join(self.skills_dir_v1, d))]
        self.assertGreaterEqual(len(skill_folders), 200, "Should have at least 200 distinct skill modules")

    def test_skill_md_files_contain_frontmatter(self):
        skill_folders = [os.path.join(self.skills_dir_v1, d) for d in os.listdir(self.skills_dir_v1) if os.path.isdir(os.path.join(self.skills_dir_v1, d))]
        valid_count = 0
        for folder in skill_folders:
            skill_md = os.path.join(folder, "SKILL.md")
            if os.path.exists(skill_md):
                with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if content.startswith("---") or "name:" in content or "# " in content:
                        valid_count += 1

        self.assertGreaterEqual(valid_count, 200, "At least 200 skills must have valid SKILL.md documentation")

if __name__ == "__main__":
    unittest.main()
