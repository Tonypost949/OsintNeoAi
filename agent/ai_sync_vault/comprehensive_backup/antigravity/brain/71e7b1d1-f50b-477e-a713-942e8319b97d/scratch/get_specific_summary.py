import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_path = os.path.join(scratch_dir, "anaheim_gilbert_east_covenant_matches.txt")

if not os.path.exists(txt_path):
    print("Matches text file does not exist!")
    os._exit(1)

with open(txt_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's split by "========================================================================"
blocks = content.split("========================================================================\n")

print(f"Total blocks in file: {len(blocks)}")

# Let's print out the blocks that contain certain words
interest_words = ["gilbert", "east st", "covenant", "nunez", "barnes"]

for b in blocks:
    if "KEYWORD MATCH:" in b:
        # Check if it contains Gilbert St or East St or Covenant House
        b_lower = b.lower()
        if "gilbert" in b_lower or "east st" in b_lower or "covenant" in b_lower:
            print("\n---------------- MATCH BLOCK START ----------------")
            # Print first 2000 chars of the block safely
            safe_b = b.encode('ascii', 'backslashreplace').decode('ascii')
            print(safe_b[:2500])
            print("---------------- MATCH BLOCK END ----------------\n")
