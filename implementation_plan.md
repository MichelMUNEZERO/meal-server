# Meal Access & QR Attendance Management System — Frontend

A modern, mobile-first SvelteKit frontend for managing meal plans, QR-based attendance, and admin operations. Connects to a Django REST backend with Supabase database.

## User Review Required

> [!IMPORTANT]
> **Admin credentials**: The admin password `Mich540el12!` will be used as a default seed — it will NOT be hardcoded in the frontend. The login flow calls the Django REST API for authentication.

> [!WARNING]
> **No Django backend exists yet.** This plan builds the **frontend only** with mock API service layers so you can see the full UI immediately. When the Django REST API is ready, you swap the mock services for real `fetch()` calls.

> [!IMPORTANT]
> **Node.js is not installed** on your system. Step 1 will install Node.js 20 LTS via the NodeSource repository.

## Open Questions

1. **Color scheme preference?** I'll use a clean teal/emerald + dark navy palette (professional, food-service appropriate). Let me know if you prefer different colors.
2. **QR code format**: I'll use `qrcode` npm package to generate QR codes client-side. The QR payload will be a JSON token `{userId, mealType, timestamp, signature}`. Is that acceptable?
3. **Supabase direct access?** Since the backend is Django REST, I assume the frontend only talks to Django APIs (not Supabase directly). Confirm?

---

## Proposed Changes

### 1. Environment Setup

Install Node.js 20 LTS on Ubuntu 24.04 via NodeSource, then scaffold a SvelteKit project.

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create SvelteKit project
npx -y sv create ./  # in /home/michel-munezero/Documents/Projects/Trackers
npm install
```

**Additional dependencies:**
- `qrcode` — QR code generation
- `xlsx` — Excel file parsing (admin upload) & export
- `lucide-svelte` — Lightweight icon library

---

### 2. Project Structure

```
Trackers/
├── src/
│   ├── lib/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── Card.svelte
│   │   │   ├── DataTable.svelte
│   │   │   ├── Modal.svelte
│   │   │   ├── Toast.svelte
│   │   │   ├── QRCode.svelte
│   │   │   ├── FileUpload.svelte
│   │   │   ├── Pagination.svelte
│   │   │   ├── SearchFilter.svelte
│   │   │   ├── StatusBadge.svelte
│   │   │   └── Sidebar.svelte
│   │   ├── stores/              # Svelte stores
│   │   │   ├── auth.js
│   │   │   ├── toast.js
│   │   │   └── theme.js
│   │   ├── services/            # API service layer (mock → real)
│   │   │   ├── api.js           # Base fetch wrapper
│   │   │   ├── auth.service.js
│   │   │   ├── users.service.js
│   │   │   ├── meals.service.js
│   │   │   ├── attendance.service.js
│   │   │   └── mock-data.js     # Mock data for demo
│   │   └── utils/
│   │       ├── constants.js
│   │       └── helpers.js
│   ├── routes/
│   │   ├── +layout.svelte       # Root layout (nav, toast container)
│   │   ├── +page.svelte         # Landing / redirect
│   │   ├── login/
│   │   │   └── +page.svelte     # Login page
│   │   ├── forgot-password/
│   │   │   └── +page.svelte     # Forgot password
│   │   ├── dashboard/           # User dashboard
│   │   │   ├── +layout.svelte   # Dashboard shell (sidebar + topbar)
│   │   │   ├── +page.svelte     # Profile + meal plan overview
│   │   │   ├── qr/
│   │   │   │   └── +page.svelte # QR code generator
│   │   │   └── history/
│   │   │       └── +page.svelte # Attendance history
│   │   └── admin/               # Admin panel
│   │       ├── +layout.svelte   # Admin shell
│   │       ├── +page.svelte     # Admin overview / stats
│   │       ├── users/
│   │       │   └── +page.svelte # User management table
│   │       ├── meals/
│   │       │   └── +page.svelte # Meal package assignment
│   │       ├── attendance/
│   │       │   └── +page.svelte # Attendance logs
│   │       └── upload/
│   │           └── +page.svelte # Excel import
│   └── app.html
├── static/
│   └── favicon.png
├── package.json
└── svelte.config.js
```

---

### 3. Pages & Features

#### Authentication Pages
| Page | Features |
|------|----------|
| **Login** | Email + password form, validation, error toasts, "Forgot Password" link, responsive card layout |
| **Forgot Password** | Email input, success confirmation, back-to-login link |

#### User Dashboard
| Page | Features |
|------|----------|
| **Profile Overview** | Name, email, access days remaining (progress bar), assigned meal plan cards (B/L/D) |
| **QR Code** | Generate single active QR, show validity status badge, auto-expire indicator, regenerate button |
| **Attendance History** | Sortable table with date, meal type, check-in time; pagination; date filter |

#### Admin Dashboard
| Page | Features |
|------|----------|
| **Overview** | Stats cards (total users, active today, meals served), quick-action buttons |
| **Users** | Full data table with search, filter, pagination; inline status badges; edit/assign actions |
| **Meal Assignment** | Per-user meal package config, access days setter, bulk actions |
| **Attendance Logs** | Filterable by date range + user; exportable to Excel; pagination |
| **Excel Upload** | Drag-and-drop file upload zone, preview table, confirm import |

---

### 4. Design System

| Token | Value |
|-------|-------|
| **Primary** | `#0D9488` (teal-600) |
| **Primary Dark** | `#0F766E` |
| **Accent** | `#F59E0B` (amber-500) |
| **Background** | `#F8FAFC` (light), `#0F172A` (dark) |
| **Surface** | `#FFFFFF` (light), `#1E293B` (dark) |
| **Text** | `#1E293B` (light), `#F1F5F9` (dark) |
| **Error** | `#EF4444` |
| **Success** | `#22C55E` |
| **Font** | Inter (Google Fonts) — 400, 500, 600, 700 |
| **Border radius** | `8px` cards, `6px` buttons, `12px` modals |
| **Shadows** | Subtle, layered (`0 1px 3px rgba(0,0,0,0.1)`) |

**Mobile-first breakpoints:** `480px`, `768px`, `1024px`, `1280px`

---

### 5. Key Technical Decisions

1. **Mock API layer**: All services return Promises wrapping mock data. A single `USE_MOCK` flag switches to real API calls.
2. **QR generation**: Client-side using `qrcode` library — no server round-trip needed for QR rendering.
3. **Excel handling**: `xlsx` (SheetJS) for both parsing uploads and generating downloads — runs entirely in-browser.
4. **Auth store**: Svelte writable store with `localStorage` persistence for session tokens.
5. **Toast system**: Global store-driven notification system with auto-dismiss.
6. **No heavy animations**: CSS transitions only (transform, opacity) — no animation libraries.
7. **Lightweight icons**: `lucide-svelte` tree-shakes to only include used icons.

---

## Verification Plan

### Automated Tests
```bash
npm run dev          # Start dev server
npm run build        # Verify production build succeeds
```

### Manual Verification (Browser)
- [ ] Login page renders, form validation works
- [ ] User dashboard shows profile, meal cards, QR code
- [ ] QR code generates and displays correctly
- [ ] Attendance history table with pagination
- [ ] Admin dashboard stats cards
- [ ] Admin user table with search/filter/pagination
- [ ] Excel upload with file preview
- [ ] Excel download for attendance reports
- [ ] Toast notifications appear and auto-dismiss
- [ ] Responsive layout on mobile viewport (375px)
- [ ] Dark/light theme toggle (if included)
- [ ] Navigation between all pages works
