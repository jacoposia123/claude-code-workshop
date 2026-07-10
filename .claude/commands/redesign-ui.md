---
description: Redesign the app UI to a modern SaaS-style layout with a dark vertical sidebar replacing the top nav bar
---

# /redesign-ui

Transforms the current horizontal top-nav layout into a modern SaaS-style interface with a fixed dark vertical sidebar.

## What changes

- `client/src/App.vue` — full layout rewrite (sidebar + content column)
- `client/src/components/FilterBar.vue` — update sticky position from `top: 70px` to `top: 0`

CLAUDE.md mandates delegating ALL `.vue` file work to `vue-expert`. Follow that rule for both files below.

---

## Step 1 — Rewrite App.vue (delegate to vue-expert)

Delegate to vue-expert with the following exact instructions:

**Rewrite `client/src/App.vue` to implement a dark vertical sidebar layout.**

### Root layout

The `.app` root element becomes a flex row:

```css
.app {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f8fafc;
}
```

Remove the `.top-nav`, `.nav-container`, and `.nav-tabs` elements and all their CSS entirely.

### Sidebar

Add a `.sidebar` element as the first child of `.app`:

```html
<aside class="sidebar">
  <!-- Brand -->
  <div class="sidebar-brand">
    <div class="sidebar-logo">F</div>
    <div class="sidebar-brand-text">
      <span class="sidebar-title">FactoryIMS</span>
      <span class="sidebar-subtitle">Management System</span>
    </div>
  </div>

  <!-- Navigation -->
  <nav class="sidebar-nav">
    <router-link to="/" class="nav-item" exact-active-class="active">
      <!-- SVG: grid icon -->
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
      </svg>
      <span>Overview</span>
    </router-link>

    <router-link to="/inventory" class="nav-item" active-class="active">
      <!-- SVG: box icon -->
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
      </svg>
      <span>Inventory</span>
    </router-link>

    <router-link to="/orders" class="nav-item" active-class="active">
      <!-- SVG: clipboard list icon -->
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
        <rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/>
        <line x1="9" y1="16" x2="13" y2="16"/>
      </svg>
      <span>Orders</span>
    </router-link>

    <router-link to="/spending" class="nav-item" active-class="active">
      <!-- SVG: bar chart icon -->
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="16"/><line x1="2" y1="20" x2="22" y2="20"/>
      </svg>
      <span>Finance</span>
    </router-link>

    <router-link to="/demand" class="nav-item" active-class="active">
      <!-- SVG: trending up icon -->
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
        <polyline points="17 6 23 6 23 12"/>
      </svg>
      <span>Demand Forecast</span>
    </router-link>

    <router-link to="/reports" class="nav-item" active-class="active">
      <!-- SVG: file bar chart icon -->
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="9" y1="15" x2="9" y2="18"/><line x1="12" y1="12" x2="12" y2="18"/>
        <line x1="15" y1="9" x2="15" y2="18"/>
      </svg>
      <span>Reports</span>
    </router-link>
  </nav>

  <!-- Footer -->
  <div class="sidebar-footer">
    <LanguageSwitcher />
    <ProfileMenu @show-profile-details="showProfileDetails = true" @show-tasks="showTasks = true" />
  </div>
</aside>
```

### Content area

Replace the old `<main class="main-content">` wrapper with:

```html
<div class="app-content">
  <FilterBar />
  <main class="main-content">
    <router-view />
  </main>
</div>
```

### Sidebar CSS (scoped)

```css
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 240px;
  height: 100vh;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  z-index: 100;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar-logo {
  width: 32px;
  height: 32px;
  background: #2563eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.sidebar-brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sidebar-title {
  color: #f1f5f9;
  font-weight: 600;
  font-size: 0.875rem;
  line-height: 1.2;
  white-space: nowrap;
}

.sidebar-subtitle {
  color: #475569;
  font-size: 0.7rem;
  line-height: 1.2;
  white-space: nowrap;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.813rem;
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
}

.nav-item.active {
  background: rgba(37, 99, 235, 0.15);
  color: #ffffff;
  border-left-color: #2563eb;
}

.nav-item svg {
  flex-shrink: 0;
  opacity: 0.8;
}

.nav-item.active svg {
  opacity: 1;
}

.sidebar-footer {
  padding: 0.75rem 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-content {
  margin-left: 240px;
  flex: 1;
  height: 100vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 1.5rem 2rem;
  max-width: 1600px;
  width: 100%;
}
```

Also update the ProfileMenu and LanguageSwitcher styles inside the sidebar footer so their dropdowns open upward. Both components use `.dropdown-menu` positioned absolutely. In the sidebar footer context, add `bottom: 100%; top: auto;` to their dropdown positioning. The cleanest way is to wrap them in a container that has `position: relative` — which both already have.

---

## Step 2 — Update FilterBar.vue (delegate to vue-expert)

Delegate to vue-expert with these instructions:

In `client/src/components/FilterBar.vue`, make two CSS changes:

1. Change the sticky positioning from `top: 70px` to `top: 0`
2. Add `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06)` to the `.filters-bar` element

No other changes.

---

## Step 3 — Verify with Playwright

After vue-expert completes both files:

1. Use `mcp__playwright__navigate` to go to `http://localhost:3000`
2. Use `mcp__playwright__screenshot` to confirm the sidebar renders correctly
3. Click each nav link and confirm the route changes
4. Confirm the FilterBar is visible below the content top edge (not behind sidebar)
5. Open ProfileMenu and LanguageSwitcher — confirm dropdowns appear correctly
