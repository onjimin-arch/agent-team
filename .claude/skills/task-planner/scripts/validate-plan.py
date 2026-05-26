import json
import re
from pathlib import Path

PLAN_PATH = Path('output/plan.md')


def load_plan(path=PLAN_PATH):
    if not path.exists():
        raise FileNotFoundError(f'Plan file not found: {path}')
    return path.read_text(encoding='utf-8')


def parse_assignments(text):
    assignments = []
    current = None
    for line in text.splitlines():
        heading = re.match(r'^### Assignment \d+: (.+)$', line)
        if heading:
            if current:
                assignments.append(current)
            current = {'member': heading.group(1).strip(), 'dependencies': []}
            continue
        if current is None:
            continue
        dep = re.search(r'^- 의존성: (.+)$', line)
        if dep:
            current['dependencies'] = [x.strip() for x in dep.group(1).split(',') if x.strip() and x.strip().lower() != '없음']
    if current:
        assignments.append(current)
    return assignments


def validate_dag(assignments):
    graph = {a['member']: a['dependencies'] for a in assignments}
    visited = set()
    path = set()

    def dfs(node):
        if node in path:
            return False
        if node in visited:
            return True
        path.add(node)
        for dep in graph.get(node, []):
            if dep not in graph:
                raise ValueError(f'Unknown dependency: {dep}')
            if not dfs(dep):
                return False
        path.remove(node)
        visited.add(node)
        return True

    return all(dfs(node) for node in graph)


def main():
    text = load_plan()
    assignments = parse_assignments(text)
    if len(assignments) == 0:
        raise ValueError('No assignments found in plan.md')
    if not validate_dag(assignments):
        raise ValueError('Dependency cycle detected in plan.md')
    print('Plan validation passed.')


if __name__ == '__main__':
    main()
