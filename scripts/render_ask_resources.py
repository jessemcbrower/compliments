import json
import os
import sys

def main():
    skill_id = os.getenv("SKILL_ID")
    if not skill_id:
        print("SKILL_ID is not set", file=sys.stderr)
        sys.exit(1)

    path = "ask-resources.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    profiles = data.setdefault("profiles", {}).setdefault("default", {})
    profiles["skillId"] = skill_id

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print("Updated ask-resources.json with SKILL_ID")

if __name__ == "__main__":
    main()

