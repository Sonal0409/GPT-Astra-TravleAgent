# Autonomous AI Travel Agent

A local Flask presentation demo using the OpenAI Responses API, strict function schemas, simulated Singapore inventory and a streamed browser activity feed.

## Start tomorrow

From this folder in PowerShell:

```powershell
.\start-demo.cmd
```

Open http://127.0.0.1:5000 and click **Start autonomous planning**. Keep the terminal running. Stop with Ctrl+C. The Present button enables fullscreen.

Your API key stays in `.env` (gitignored). Internet access and available OpenAI API credit are required. The app reloads `.env` before each run. `OPENAI_MODEL` defaults to `gpt-5.4-mini`.

## Architecture

- `app.py`: loopback-only Flask server; POST `/api/run` returns newline-delimited JSON events.
- `agent.py`: Responses API loop; model output function calls are validated, executed, and returned with matching `call_id` as `function_call_output`. Full response output is retained server-side between turns. No reasoning items are sent to the browser.
- `travel.py`: deterministic search inventory and independent cost arithmetic. No budget branch selects an alternative.
- `templates/` and `static/`: dark responsive presentation interface, live public tool trace, budget comparison, itinerary and JSON export.

The prompt deliberately asks for a comfortable recommended baseline before optimization so the presentation demonstrates failure and adaptation. It does **not** specify the replacement IDs or target total. The model sees the failed check, chooses its strategy and search calls, and selects the next combination. Only prices are deterministic: wording and exact tool sequence can vary. There is no scripted fallback pretending to be AI.

The final tool refuses over-budget plans, unseen inventory IDs, combinations not matching the latest budget check, or itineraries missing days. The model must faithfully extract user constraints; this is a scoped demo, not a hardened booking or arbitrary-goal validation service. Other destinations are unsupported. It can report infeasible rather than loop forever; runs are limited to 32 model turns.

## Singapore scenario

Assumptions: Mumbai departure, flexible dates, 4 adults, 5 days / 4 nights, 2 twin rooms. Simulated fares include taxes. No booking occurs.

| Component | Comfortable baseline | Value combination |
|---|---:|---:|
| Round-trip flights | 88,000 | 68,000 |
| Rooms, 4 nights | 48,000 | 28,000 |
| Food | 18,000 | 18,000 |
| Local transport | 7,000 | 5,000 |
| Sightseeing | 10,000 | 10,000 |
| Visa/insurance allowance | 10,000 | 10,000 |
| Contingency | 4,000 | 4,000 |
| **Total (INR)** | **185,000** | **143,000** |

Trade-offs: early direct flight with cabin baggage, compact private rooms near MRT, public transport and hawker dining. Visa/insurance amounts are fictional budgeting allowances, not current legal or price guidance.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe verify_live.py
```

The first command runs offline unit/integration checks. The second spends API tokens and asserts a real failed first check, a model replanning call, a successful budget, and a five-day completion. Public evidence is saved to `artifacts/live-run.json`; this is a test record, not a replay mode. Use **Export run** in the completed browser result to save another trace.

For a fresh installation with Python 3.12+:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Create `.env` from `.env.example` if missing. Do not commit or share `.env`.

API integration reference: https://developers.openai.com/api/docs/guides/function-calling
