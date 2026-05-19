# Meal Trackers

QR-based meal access and attendance frontend built with **SvelteKit 2** and **Svelte 5**. Designed to connect to a **Django REST** backend (integration points are marked in the codebase).

## Features

- **Member dashboard** — meal plan overview, rotating QR codes, attendance history
- **Admin panel** — users, meal packages, attendance export, bulk Excel import
- **Scanner** — camera QR verification with session log
- **Auth** — login, forgot password, reset password (token link), change password in account settings
- **Mock API layer** — full UI works offline until `VITE_USE_MOCK=false`

## Quick start

```bash
npm install
cp .env.example .env
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### Development accounts (mock mode only)

| Role    | Email                 | Password     |
|---------|-----------------------|--------------|
| Member  | michel@example.com    | password     |
| Admin   | admin@trackers.com    | admin123     |
| Scanner | scanner@trackers.com  | scanner123   |

Do not use these credentials in production.

## Backend integration

1. Set `VITE_API_BASE_URL` to your Django API root.
2. Set `VITE_USE_MOCK=false`.
3. Implement endpoints referenced in `src/lib/services/` (search for `Backend integration point`).

Core services:

- `auth.service.js` — login / logout
- `users.service.js` — CRUD, password reset, change password
- `meals.service.js` — meal plan per user
- `attendance.service.js` — history, QR generation, scan verification

## Scripts

| Command        | Description              |
|----------------|--------------------------|
| `npm run dev`  | Development server       |
| `npm run build`| Production build         |
| `npm run check`| Typecheck / svelte-check |

## Project structure

```
src/
  lib/
    components/   # UI building blocks
    services/     # API layer (mock + real)
    stores/       # Auth, toast, scanner session
    utils/        # Guards, helpers, constants
  routes/         # SvelteKit pages
```

## License

Private — Michel Munezero.
