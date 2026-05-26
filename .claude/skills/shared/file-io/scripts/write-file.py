from pathlib import Path


def write_file(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')


def main():
    print('Use write_file(path, content) to save file content.')


if __name__ == '__main__':
    main()
