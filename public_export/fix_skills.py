import os

paths = [
    r"C:\OsintNeoAi\.agents\skills",
    r"C:\.agents\skills",
    r"C:\Users\Amd949609\.agents\skills"
]

for base_path in paths:
    if not os.path.exists(base_path):
        continue
    for skill_dir in os.listdir(base_path):
        skill_path = os.path.join(base_path, skill_dir, "SKILL.md")
        if os.path.exists(skill_path):
            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if not content.startswith("---"):
                name = skill_dir
                # Try to extract the first # Header as description
                description = f"{name} skill"
                for line in content.split("\n"):
                    if line.startswith("# "):
                        description = line[2:].strip()
                        break
                
                frontmatter = f"---\nname: {name}\ndescription: {description}\n---\n"
                
                with open(skill_path, "w", encoding="utf-8") as f:
                    f.write(frontmatter + content)
                print(f"Fixed {skill_path}")
