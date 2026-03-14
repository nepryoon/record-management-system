# Contributing Guide

## Commit Message Standard

This project follows a Conventional Commits style.  
A commit template is provided in `.gitmessage`.  
Activate it locally with:

```bash
git config commit.template .gitmessage
```

### Format

```
<type>(<scope>): <subject>
```

| Type       | When to use                              |
|------------|------------------------------------------|
| `feat`     | A new feature                            |
| `fix`      | A bug fix                                |
| `docs`     | Documentation changes only               |
| `style`    | Formatting, whitespace (no logic change) |
| `refactor` | Code restructuring (no feature/fix)      |
| `test`     | Adding or updating tests                 |
| `chore`    | Build process, dependency updates, etc.  |

- **Subject**: imperative present tense, no full stop, ≤ 72 characters.
- **Body** (optional): wrap at 72 characters; explain *what* and *why*.
- **Footer** (optional): `Refs: #<issue>`, `BREAKING CHANGE: <description>`.

### Examples

```
feat(client): add cascade delete for associated flight records

When a Client record is deleted, all Flight records whose
Client_ID matches the deleted client are now also removed.

Refs: #12
```

```
fix(storage): correct default JSONL file path to data/records.jsonl
```

```
test(flight): add canonical schema key assertions
```
