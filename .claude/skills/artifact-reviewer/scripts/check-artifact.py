import json
import re
from pathlib import Path


REQUIRED_SECTION_PATTERN = re.compile(r'^#+\s*(.+)$')


def read_file(path):
    return Path(path).read_text(encoding='utf-8')


def extract_sections(text):
    sections = []
    for line in text.splitlines():
        match = REQUIRED_SECTION_PATTERN.match(line)
        if match:
            sections.append(match.group(1).strip())
    return sections


def validate_markdown(path, required_sections):
    text = read_file(path)
    sections = extract_sections(text)
    missing = [s for s in required_sections if s not in sections]
    return missing


def validate_json(path, schema=None):
    data = json.loads(read_file(path))
    if schema is None:
        return []
    schema_data = json.loads(Path(schema).read_text(encoding='utf-8'))
    # Basic JSON schema placeholder: check required keys only
    missing = []
    for key in schema_data.get('required', []):
        if key not in data:
            missing.append(key)
    return missing


def main():
    print('This script validates artifacts by basic structure.')


if __name__ == '__main__':
    main()
