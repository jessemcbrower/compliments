import json
import os
import sys

def main():
    arn = os.getenv("LAMBDA_ARN")
    if not arn:
        print("LAMBDA_ARN is not set", file=sys.stderr)
        sys.exit(1)

    skill_path = os.path.join("skill-package", "skill.json")
    with open(skill_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    endpoint = manifest.get("manifest", {}).get("apis", {}).get("custom", {}).get("endpoint", {})
    if not endpoint:
        print("Invalid skill manifest structure", file=sys.stderr)
        sys.exit(1)

    endpoint["uri"] = arn

    with open(skill_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print("Updated skill manifest with LAMBDA_ARN")

if __name__ == "__main__":
    main()

