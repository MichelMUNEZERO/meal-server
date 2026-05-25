# Meal System API Documentation

This document describes the HTTP API for the Meal System project. It includes authentication, role rules, endpoint descriptions, request/response examples, error codes, and example curl workflows for admin, scanner, and regular user flows.

**Base URL:** `http://127.0.0.1:8000/`

**Auth scheme:** Bearer token. Obtain a token by POSTing to `/api/auth/login/` and include it in `Authorization: Bearer <token>` for protected endpoints.

**Roles:**
- `user` — regular member
- `admin` — administrator (can manage users and view all meal plans)
- `scanner` — scanner role (can verify scans)


**Common error responses:**
- `401 Authentication required` — no valid token provided
- `403 You do not have permission to access this resource` — authenticated but role not allowed
- `400` — bad request / validation error
- `404` — resource not found
- `405` — wrong HTTP method


**Authentication / Account endpoints**

- **Login**
  - URL: `POST /api/auth/login/`
  - Auth: none
  - Body (JSON):
    ```json
    { "email": "user@example.com", "password": "secret" }
    ```
  - Success response (200):
    ```json
    {
      "success": true,
      "user": { "id": 2, "name": "Michel", "email": "michel@example.com", "role": "user", "plan": "B/L" },
      "token": "<token>"
    }
    ```
  - Notes: must use `POST`. Visiting this URL in the browser (GET) returns `405 Method not allowed`.

- **Logout**
  - URL: `POST /api/auth/logout/`
  - Auth: Bearer token required
  - Body: none
  - Success: `200` with `{ "success": true }`

- **Password reset request**
  - URL: `POST /api/auth/password-reset/`
  - Body: `{ "email": "user@example.com" }`
  - Success: `200` with a safe message (link generation handled server-side)

- **Password reset confirm**
  - URL: `POST /api/auth/password-reset/confirm/`
  - Body: `{ "token": "...", "password":"newpass" }`

- **Change password (authenticated)**
  - URL: `POST /api/auth/change-password/`
  - Auth: Bearer token
  - Body: `{ "current_password":"old", "new_password":"newpass" }`

- **Session**
  - URL: `GET|POST /api/session` or `/api/session/`
  - Auth: Bearer token
  - `POST` body: `{ "sessionId": "..." }` sets a device session id
  - `GET` returns the stored `activeSession` id for the bearer user (or for a specified `userId` if allowed)


**Users endpoints**

- **List users**
  - URL: `GET /api/users/`
  - Auth: Bearer token
  - Allowed roles: `admin`, `scanner`, `user`
  - Query parameters:
    - `?role=admin|scanner|user` — filter by role
    - `?status=Active|Inactive` — filter by status
  - Returns all users (or filtered by role/status if specified)

- **Create user**
  - URL: `POST /api/users/create/`
  - Auth: Bearer token
  - Allowed roles: `admin`
  - Body (JSON):
    ```json
    {
      "name": "John Doe",
      "email": "john@example.com",
      "password": "securepassword123",
      "phone": "0700000000",
      "registration_number": "REG-001",
      "role": "admin|scanner|user",
      "status": "Active|Inactive"
    }
    ```
  - Required fields: `name`, `email`, `password`
  - Optional fields: `phone`, `registration_number`, `role` (defaults to `user`), `status` (defaults to `Active`)
  - Success response (200):
    ```json
    {
      "success": true,
      "user": { ... user object ... }
    }
    ```
  - Errors:
    - `400` — missing/invalid fields, email already exists, password too short
    - `401` — not authenticated
    - `403` — not an admin

- **Bulk import users**
  - URL: `POST /api/users/bulk-import/`
  - Auth: Bearer token
  - Allowed roles: `admin`
  - Uploads may be sent as a file named `file` or `excel`.
  - The importer uses Pandas to read and study the spreadsheet before creating accounts.
  - Excel header order does not matter; the importer matches common header aliases such as `Full Name`, `E-mail`, `Reg #`, and `Contact Number`.
  - The importer can also recover from extra title rows or slightly messy layouts by inferring the correct columns before creating accounts.
  - Required fields: `name`, `email`, `phone`, and `registration_number`.
  - If any required field is missing in a row, that row is skipped with a validation error.
  - For each created account, the system generates a temporary password, creates a reset token, and sends the credentials to the user email address.

- **User detail**
  - URL: `GET /api/users/<user_id>/` (read), `PATCH /api/users/<user_id>/` (update)
  - Auth: Bearer token
  - Allowed roles for view: admin/scanner/user (view) — updates require `admin`
  - PATCH body fields: `name`, `email`, `status` (`Active|Inactive`), `role` (`admin|scanner|user`)
  - Example: Update a user to scanner role
    ```json
    { "role": "scanner", "status": "Active" }
    ```

- **Send password reset (admin)**
  - URL: `POST /api/users/<user_id>/send-password-reset/`
  - Auth: Bearer token
  - Allowed roles: `admin`


**Meals endpoints**

- **User meal plan**
  - URL: `GET|PUT|PATCH /api/users/<user_id>/meal-plan/`
  - Auth: Bearer token
  - Allowed roles: `admin`, `user`, `scanner`
  - GET: returns the event-day summary and meal access fields for the user
  - PUT/PATCH: accepted fields: `breakfast`, `lunch`, `dinner` (boolean), `daysRemaining`, `totalDays`, `validUntil` (ISO date or `null`)

- **All meal plans**
  - URL: `GET /api/meal-plans/`
  - Auth: Bearer token
  - Allowed roles: `admin`


**Attendance endpoints**

- **Attendance list**
  - URL: `GET /api/attendance/`
  - Auth: Bearer token
  - Allowed roles: `admin`, `user`, `scanner`
  - Optional query param: `?user=<id>` to filter

- **Generate QR**
  - URL: `POST /api/attendance/qr/`
  - Auth: Bearer token
  - Allowed roles: `admin`, `user`
  - Body (JSON): optional `{ "user_id": <id>, "meal_type": "Lunch" }`. If `user_id` omitted, current authenticated user is used.
  - Success: returns a QR payload (JSON) with fields: `userId` (string), `userName`, `mealType` (`Breakfast|Lunch|Dinner`), `timestamp` (ms since epoch), `signature` (HMAC SHA256). Example:
    ```json
    {
      "userId": "2",
      "userName": "Michel",
      "mealType": "Lunch",
      "timestamp": 1716000000000,
      "signature": "..."
    }
    ```
  - Signature is created using `hmac.new(settings.SECRET_KEY, message, sha256)` where message=`"{userId}|{mealType}|{timestamp}"`.

- **Verify scan**
  - URL: `POST /api/attendance/verify/`
  - Auth: Bearer token
  - Allowed roles: `admin`, `scanner` (by default)
  - Body: `{ "payload": { ... } }` where `payload` is the QR payload produced by `generate_qr`
  - Verification checks performed (in order):
    - payload has `userId`, `mealType`, `timestamp`, `signature`
    - signature matches expected HMAC
    - timestamp within QR expiry (default 30 seconds)
    - a meal window is currently active (see `MEAL_WINDOWS` below)
    - `mealType` matches the current active window
    - user exists
    - user has not checked in already for that meal today (unique constraint)
  - Success: returns `success` with `user`, `mealType`, and `record` data
  - Possible errors: `400` invalid payload/signature/expired/not active; `403` if role not allowed; `401` if unauthenticated

**Meal windows and QR expiry**
- Meal windows defined in `meal_system/api_utils.py::MEAL_WINDOWS` (default values):
  - Breakfast 06:00 - 11:50
  - Lunch     12:00 - 17:30
  - Dinner    18:00 - 22:00
- QR expiry constant: `QR_EXPIRY_SECONDS = 30` (seconds). QR older than this will be rejected.
- A QR can be scanned only once for a given meal period. If the same QR is scanned again, the API will respond that the QR code has already been used.
- The QR payload is regenerated on its normal refresh cycle, so users should generate a new QR when they need to scan again.


**Signature details**
- The signature used in QR payloads is HMAC SHA-256 of the message: `{userId}|{mealType}|{timestamp}` using the Django `SECRET_KEY` as the HMAC key.
- Example Python snippet used by the server (for reference):
```py
import hmac, hashlib
message = f"{user_id}|{meal_type}|{timestamp}"
signature = hmac.new(settings.SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
```


**Sample curl workflows**

1) Login → list users (scanner)
```bash
# Login (POST) -> get token
curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"scanner@trackers.com","password":"scanner123"}' | jq

# Use token from response (replace <token>)
curl -s -X GET http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Bearer <token>" | jq
```

2) User generates QR for themselves (michel)
```bash
# Login as michel
curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"michel@example.com","password":"password"}' | jq

# Generate QR (replace <token>)
curl -s -X POST http://127.0.0.1:8000/api/attendance/qr/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{}' | jq
```

3) Scanner verifies QR
```bash
# Login as scanner (get token)
# Suppose we have the QR payload from step 2 in payload.json
curl -s -X POST http://127.0.0.1:8000/api/attendance/verify/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <scanner-token>" \
  -d '{"payload": <insert-qr-payload-here>}' | jq
```

Notes:
- Replace `<token>` with the `token` field returned by `/api/auth/login/`.
- Use a JSON tool like `jq` to pretty-print responses.


**Troubleshooting / common pitfalls**
- Visiting POST-only endpoints in a browser will show `{"detail":"Method not allowed"}` because the browser issues GET requests from the address bar.
- Browser login to Django Admin does not create the API Bearer token; you must call `/api/auth/login/` (POST) to receive a token for API requests.
- If login returns `This account is inactive`, check the `UserProfile.status` and the Django `User.is_active` flag. Some seeded demo accounts are inactive by design (e.g. `jane@example.com`).
- If an authenticated user sees `You do not have permission to access this resource`, their role is not permitted by the view's `@require_auth(roles=[...])` decorator.


**Optional changes**
- To allow regular users to verify scans directly (if desired), edit `attendance/views.py` and change the `verify_scan` decorator to:
```py
@require_auth(roles=[UserProfile.ROLE_ADMIN, UserProfile.ROLE_SCANNER, UserProfile.ROLE_USER])
```
This will permit `ROLE_USER` to call `/api/attendance/verify/` with a valid token.


**Seeded demo accounts (created by `users/signals.py` on migrate)**
- Admin: admin@trackers.com / admin123 (is_staff, is_superuser)
- Scanner: scanner@trackers.com / scanner123 (ROLE_SCANNER)
- Member: michel@example.com / password (ROLE_USER)
- John: john@example.com / password (ROLE_USER)
- Jane: jane@example.com / password (ROLE_USER) — **inactive**


---

Generated from code in the repository (endpoints and behavior examined in `users/views.py`, `attendance/views.py`, `meals/views.py`, and `meal_system/api_utils.py`).

If you want, I can also:
- add an OpenAPI/Swagger spec file (YAML/JSON) for import into tools like Swagger UI or Postman, or
- create a `scripts/` folder with example curl scripts for admin/scanner/user flows.


---

## Admin User Management Guide

### Overview
Administrators can create, modify, and manage users through the API. This includes creating new scanners, other admins, and regular users, as well as changing their roles and status.

### Creating Users via API

**Create a single user:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "name": "John Scanner",
    "email": "john.scanner@example.com",
    "password": "securepassword123",
    "phone": "0700000001",
    "registration_number": "SCAN-001",
    "role": "scanner",
    "status": "Active"
  }'
```

**Create an admin user:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{
    "name": "Jane Admin",
    "email": "jane.admin@example.com",
    "password": "securepw123",
    "role": "admin",
    "status": "Active"
  }'
```

### Listing Users by Role

**List all scanners:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?role=scanner" \
  -H "Authorization: Bearer <admin-token>"
```

**List all admins:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?role=admin" \
  -H "Authorization: Bearer <admin-token>"
```

**List all active users:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?status=Active" \
  -H "Authorization: Bearer <admin-token>"
```

### Changing User Roles

**Promote a user to scanner:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/users/<user_id>/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{ "role": "scanner" }'
```

**Promote a user to admin:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/users/<user_id>/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{ "role": "admin" }'
```

**Demote a user:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/users/<user_id>/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{ "role": "user" }'
```

### Managing User Status

**Deactivate a user:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/users/<user_id>/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{ "status": "Inactive" }'
```

**Reactivate a user:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/users/<user_id>/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-token>" \
  -d '{ "status": "Active" }'
```

### Command-Line User Management

**Create a user via command line:**
```bash
python3 manage.py create_user john.doe@example.com "John Doe" --password "securepassword123" --phone "0700000001" --role scanner
```

**Create a user with generated password:**
```bash
python3 manage.py create_user jane.admin@example.com "Jane Admin" --role admin --generate-password
```

### Admin Helpers (Python)

For programmatic user management in custom scripts or Django shell:

```python
from users.admin_helpers import create_admin_user, create_scanner_user, update_user_role, list_users_by_role

# Create a scanner user
user = create_scanner_user(
    email='scanner@example.com',
    name='John Scanner',
    password='securepassword123',
    phone='0700000001'
)

# Create an admin user
admin = create_admin_user(
    email='admin@example.com',
    name='Jane Admin',
    password='securepw123'
)

# Update a user's role
update_user_role(user_id=5, new_role='admin')

# List all scanners
scanners = list_users_by_role('scanner')
for scanner in scanners:
    print(f"{scanner.email}: {scanner.get_full_name()}")
```

