# Architecture Overview

Factory Inventory Management System — a full-stack demo application with a Vue 3 frontend and Python FastAPI backend backed by in-memory JSON data.

---

## Tech Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Frontend framework | Vue 3 (Composition API) | ^3.4 | SFCs, composables, no class components |
| Routing | Vue Router | ^4.3 | HTML5 history mode, 6 registered routes |
| HTTP client | Axios | ^1.6 | Centralised in `client/src/api.js` |
| Build / dev server | Vite | ^5.2 | Proxies `/api` to port 8001 |
| Backend framework | FastAPI | >=0.110 | Auto-generates `/docs` (Swagger UI) |
| ASGI server | Uvicorn | >=0.24 | Entry: `uv run python main.py`, port 8001 |
| Data validation | Pydantic v2 | >=2.5 | Request/response models on all endpoints |
| Data store | JSON files + in-memory | — | Loaded once at startup; no persistence |
| Package manager (BE) | uv | — | Resolves deps from `pyproject.toml` |
| Package manager (FE) | npm | — | Resolves deps from `package.json` |
| Test runner | pytest + httpx | — | `tests/backend/` against FastAPI TestClient |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (localhost:3000)                                        │
│                                                                  │
│  ┌──────────┐  ┌──────────────────────────────────────────────┐ │
│  │ FilterBar│  │ Router View                                  │ │
│  │          │  │                                              │ │
│  │ Period   │  │  Dashboard  │ Inventory │ Orders             │ │
│  │ Location │  │  Spending   │ Demand    │ Reports            │ │
│  │ Category │  │                                              │ │
│  │ Status   │  └──────────────────────────────────────────────┘ │
│  └──────────┘                                                    │
│       │                   │                                      │
│       └─── useFilters ────┘  (singleton composable, shared state)│
│                   │                                              │
│              api.js (axios)                                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │  HTTP /api/*
                          │  (Vite dev proxy → localhost:8001)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI  (localhost:8001)                                       │
│                                                                  │
│  main.py                                                         │
│  ├── GET /api/inventory         (warehouse, category)            │
│  ├── GET /api/orders            (warehouse, category, status, month) │
│  ├── GET /api/dashboard/summary (all 4 filters)                  │
│  ├── GET /api/demand            (no filters)                     │
│  ├── GET /api/backlog           (no filters)                     │
│  ├── GET /api/spending/*        (summary, monthly, categories,   │
│  │                               transactions)                   │
│  └── GET /api/reports/*         (quarterly, monthly-trends)      │
│                                                                  │
│  mock_data.py  ──loads──▶  server/data/*.json (at startup)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Filter → API → View

```
User selects a filter (e.g. Warehouse: London)
        │
        ▼
useFilters.js  (selectedLocation ref updates)
        │
        ▼  watch triggers loadData()
View component calls api.js function
        │
        ▼
api.js builds query params, sends axios GET /api/orders?warehouse=London
        │
        ▼  (Vite proxy forwards to :8001)
FastAPI endpoint receives query params
        │
        ▼
mock_data.py in-memory list filtered in Python
        │
        ▼
Pydantic validates + serialises response
        │
        ▼
JSON response → api.js → ref in component → computed properties update → DOM re-renders
```

### Key Design Decisions

- **Raw data in refs, derived data in computed.** Views store `allOrders` in a `ref`, then use `computed` for summaries, totals, and filtered subsets. This avoids stale data bugs.
- **Global filter state via composable.** `useFilters.js` is a module-level singleton — the same refs are shared across every view and `FilterBar` without a store like Pinia/Vuex.
- **No database.** JSON files are loaded into memory by `mock_data.py` when the server starts. All filtering happens in Python. Restarts reset any mutations.
- **Vite proxy.** The frontend calls `/api/*` (relative), and Vite rewrites those to `http://localhost:8001/api/*` during development. No CORS issues, no hard-coded ports in `api.js`.

---

## File Map

```
claude-code-workshop/
├── client/
│   └── src/
│       ├── main.js               # App + router bootstrap
│       ├── App.vue               # Root layout, nav, global styles
│       ├── api.js                # All axios calls (single source of truth)
│       ├── composables/
│       │   ├── useFilters.js     # Global filter state
│       │   ├── useI18n.js        # EN/JP translations
│       │   └── useAuth.js        # Mock user + tasks
│       ├── views/
│       │   ├── Dashboard.vue     # KPIs, charts, backlog, top products
│       │   ├── Inventory.vue     # Stock table + detail modal
│       │   ├── Orders.vue        # Orders table + status cards
│       │   ├── Spending.vue      # Financial charts + transactions
│       │   ├── Demand.vue        # Forecast table
│       │   └── Reports.vue       # Quarterly + monthly aggregates
│       └── components/
│           ├── FilterBar.vue
│           ├── ProfileMenu.vue
│           ├── ProfileDetailsModal.vue
│           ├── TasksModal.vue
│           ├── InventoryDetailModal.vue
│           ├── ProductDetailModal.vue
│           ├── BacklogDetailModal.vue
│           ├── CostDetailModal.vue
│           └── LanguageSwitcher.vue
└── server/
    ├── main.py                   # All endpoints
    ├── mock_data.py              # JSON loader + in-memory store
    └── data/
        ├── inventory.json        # Stock items (SKU, qty, cost, warehouse)
        ├── orders.json           # Orders Jan–Dec 2025
        ├── demand_forecasts.json # Forecast per SKU (trend, period)
        ├── backlog_items.json    # Shortage items (priority, delay)
        ├── spending.json         # Cost breakdown (monthly, by category)
        ├── transactions.json     # Individual transactions
        └── purchase_orders.json  # Empty — PO endpoints not yet implemented
```

---

## API Endpoints Reference

| Route | Filters | Consumer |
|---|---|---|
| `GET /api/dashboard/summary` | warehouse, category, status, month | Dashboard |
| `GET /api/inventory` | warehouse, category | Inventory |
| `GET /api/orders` | warehouse, category, status, month | Orders, Dashboard |
| `GET /api/demand` | none | Demand |
| `GET /api/backlog` | none | Dashboard |
| `GET /api/spending/summary` | none | Spending |
| `GET /api/spending/monthly` | none | Spending |
| `GET /api/spending/categories` | none | Spending |
| `GET /api/spending/transactions` | none | Spending |
| `GET /api/reports/quarterly` | none | Reports |
| `GET /api/reports/monthly-trends` | none | Reports |

Interactive docs available at `http://localhost:8001/docs` when the server is running.
