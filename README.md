
# STEPS FOR CLONING 
```
cd existing_folder
git remote add origin https://github.com/ExtGroupJs/supermario_shop.git
git branch -M main
git push -uf origin main
```

# STEPS FOR DEVELOPING
1.  when the code is already cloned, create a python virtual enviroment (using currently python 3.11):
python -m venv venv

2. Activate virtual enviroment:
source /venv/bin/activate # for linux
source /venv/Scripts/activate # for windows (there's other ways too)

3. Install required packages running in the console:
pip install -r requirements.txt

4. Make a copy of REFERENCE.env in the same directory and remove the filename. Finally the file should exists with the name: .env

5. Run migrations (with this we have created a superuser):
python manage.py migrate

6. Create some dummy user objects (300):
python manage.py create_test_users

7. run server:
python manage.py runserver

8. interact with API, available on:
http://127.0.0.1:8000/api/swagger/

9. If if needed to run locally over https:
python manage.py runserver_plus --cert-file localhost.crt --key-file localhost.key


!!!For BE Develop...

pip-chill >.\req.txt

# AI / AGENT INTEGRATION (codebase-memory-mcp)

This repository ships a **knowledge graph of the codebase** built with
[codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) so both
programmers and AI agents (OpenCode, Claude Code, Cursor, etc.) can answer
structural questions — "who calls this function?", "what routes exist?" — in a
handful of tokens instead of grepping through files.

- **Local-first**: indexing and querying run 100% on your machine. No cloud, no
  API key, code never leaves your machine.
- **Django-tuned**: tracks functions, classes, call chains, and HTTP routes
  (DRF routers, `urls.py`), i.e. exactly the wiring this project depends on.

## Installing

```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

Installs the `codebase-memory-mcp` binary and auto-configures it for OpenCode,
Cursor, VS Code, and Copilot (MCP server, agents, skill). Restart your agent
session afterwards.

## How it is configured in this repo

| File | Purpose |
|------|---------|
| `opencode.json` | Registers `codebase-memory-mcp` as a local MCP server so OpenCode sessions get the graph tools automatically. |
| `.codebase-memory.json` | Project-level config for the tool (currently no `extra_extensions` needed). |
| `.codebase-memory/graph.db.zst` | Committed **team-shared index snapshot**. New teammates and fresh agent sessions bootstrap from it instead of re-indexing the whole repo. |
| `.codebase-memory/.gitattributes` | Marks the snapshot binary as `merge=ours` to avoid merge conflicts. |

## Using it

Ask your agent "index this project", or run manually:

```bash
# Full index (creates/refreshes the team snapshot)
codebase-memory-mcp cli index_repository --repo-path "$PWD" --mode full --persistence true

# One-shot CLI query
codebase-memory-mcp cli search_graph --name-pattern ".*OrderHandler.*"
```

Preferred tool order for agents (mirrored in `AGENTS.md`): `search_graph` →
`trace_path` → `get_code_snippet` → `check_index_coverage` → `query_graph` →
`get_architecture`. Visual 3D graph UI: `codebase-memory-mcp --ui=true --port=9749`.

## Regenerating the committed snapshot

`.codebase-memory/graph.db.zst` is rewritten on every explicit
`index_repository`. Commit it **deliberately** (per milestone/release), not on
every commit — each regen is a full new ~12 MB blob. To opt out entirely, add
`.codebase-memory/` to `.gitignore`; teammates will then do their own local
full index instead of bootstrapping from the snapshot.
