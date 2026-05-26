from pathlib import Path


def read_file(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'File not found: {path}')
    return p.read_text(encoding='utf-8')


def main():
    print('Use read_file(path) to load file content.')


if __name__ == '__main__':
    main()
