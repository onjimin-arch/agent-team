import csv
import json
from pathlib import Path


def parse_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def parse_csv(path):
    with Path(path).open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def parse_markdown(path):
    return Path(path).read_text(encoding='utf-8')


def main():
    print('Use parse_json, parse_csv, and parse_markdown for data parsing.')


if __name__ == '__main__':
    main()
