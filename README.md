# LunchVote — Django/DRF backend

Internal lunch voting service. Restaurants upload a daily menu; employees vote before lunch. 
Supports legacy mobile builds via `X-App-Build` header (integer).

## Tech
- Django + DRF
- JWT (djangorestframework-simplejwt)
- PostgreSQL
- Docker / docker-compose
- PyTest

## Quick start (Docker)
```bash
cp .env.example .env
docker-compose up --build
# In another terminal (first run only)
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
```
App runs at http://localhost:8000/

## Auth
- Obtain JWT: `POST /api/auth/token/` with `{"username": "...", "password": "..."}`
- Refresh JWT: `POST /api/auth/token/refresh/`

Include header `Authorization: Bearer <token>` and **`X-App-Build: <int>`** on requests.
- Legacy behavior if `X-App-Build < 200`:
  - `GET /api/menus/today/` returns `dishes` instead of `items` and `restaurant` is an id.

## API
### Employees
- `POST /api/employees/` — self-register user. Body: `username`, `password`, `first_name`, `last_name`, `email`.
- `GET /api/employees/` — list users (auth required).

### Restaurants (staff only for write)
- `POST /api/restaurants/` — create
- `GET /api/restaurants/` — list

### Menus (staff only for write)
- `POST /api/menus/` body: `{restaurant_id, date: "YYYY-MM-DD", items: [{"name":"Soup","price":5.5}]}`
  - Unique per `(restaurant, date)`
- `GET /api/menus/today/` — current day menus
- `GET /api/menus/today/results/` — vote totals per menu
- `POST /api/menus/{id}/vote/` — cast a vote for that menu (employee can vote once per menu)

## Local dev (without Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export POSTGRES_HOST=localhost POSTGRES_DB=lunchvote POSTGRES_USER=lunchvote POSTGRES_PASSWORD=lunchvote
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

## Tests & Lint
```bash
pytest
```
