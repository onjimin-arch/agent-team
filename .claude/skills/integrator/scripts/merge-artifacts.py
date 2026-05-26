from pathlib import Path


def merge_markdown(sources, target):
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open('w', encoding='utf-8') as out:
        for source in sources:
            out.write(f'# Source: {source}\n\n')
            out.write(Path(source).read_text(encoding='utf-8'))
            out.write('\n\n---\n\n')
    return target_path


def main():
    print('This script merges markdown artifacts into a final output file.')


if __name__ == '__main__':
    main()
