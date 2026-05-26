# Task Planner Skill

## Purpose
This skill helps the Team Lead decompose a task into assignments, determine dependencies, and validate the generated plan structure.

## When to Use
- Phase 1: PLAN
- When the Team Lead needs to generate or revise `/output/plan.md`

## Outputs
- Plan document with an assignment list
- Execution order
- Dependency map

## Validation
Use `validate-plan.py` to confirm:
- Assignment count is sufficient
- No cyclic dependencies
- Expected outputs are clearly mapped to members
