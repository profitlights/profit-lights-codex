import json
from pathlib import Path

from jsonschema import Draft202012Validator

BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = BASE_DIR / "schemas" / "output.schema.json"
EXAMPLES_DIR = BASE_DIR / "examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    example_files = [
        EXAMPLES_DIR / "error_friendly.example.json",
        EXAMPLES_DIR / "insight_action.example.json",
        EXAMPLES_DIR / "needs_more_info.example.json",
    ]

    failures = []
    for example_file in example_files:
        data = load_json(example_file)
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
        if errors:
            failures.append((example_file, errors))

    if failures:
        for example_file, errors in failures:
            print(f"{example_file} failed validation:")
            for error in errors:
                path = "/".join(str(item) for item in error.path)
                print(f"  - {path}: {error.message}")
        raise SystemExit(1)

    print("All example outputs are valid.")


if __name__ == "__main__":
    main()
