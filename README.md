# Movie Ticket Booking API — FastAPI Project

## About the Project

A backend REST API for a cinema ticket booking platform, built with FastAPI as part of the Innomatics Research Labs Internship (February 2026).

The system replicates a real-world movie booking experience — covering everything from movie listings and seat selection to bookings, holds, and advanced query capabilities.

---

## What It Does

### 🎬 Movie Management
- List all movies along with aggregated stats
- Fetch details for a specific movie by its ID
- Add movies with proper input validation
- Update seat availability or ticket pricing
- Delete movies (blocked if active bookings exist)

### 🎟️ Ticket Booking
- Book seats across three categories:
  - **Standard** — base price
  - **Premium** — 1.5× the base price
  - **Recliner** — 2× the base price
- Discount support via promo codes:
  - `SAVE10` — 10% off
  - `SAVE20` — 20% off
- Seat counts update automatically on booking

### 🪑 Seat Hold System
- Place a temporary hold on seats before confirming
- Convert holds into confirmed bookings
- Cancel holds and restore seat availability

### 🔍 Query & Browse
- Keyword search across movies and bookings
- Filter movies by genre, language, price range, or seat availability
- Sort results with field and direction validation
- Paginate large result sets
- A single `/browse` endpoint combining all of the above

---

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Language   | Python     |
| Framework  | FastAPI    |
| Validation | Pydantic   |
| Server     | Uvicorn    |

---

## Getting Started

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Once running, interactive API docs are available at:
**http://127.0.0.1:8000/docs**

---

## API Reference

### General

| Method | Endpoint | Description     |
|--------|----------|-----------------|
| GET    | `/`      | Welcome message |

---

### Movies

| Method | Endpoint              | Description                               |
|--------|-----------------------|-------------------------------------------|
| GET    | `/movies`             | All movies with seat stats                |
| GET    | `/movies/{movie_id}`  | Single movie by ID                        |
| GET    | `/movies/summary`     | Pricing, genre, and seat summary          |
| GET    | `/movies/filter`      | Filter by genre, language, price, seats   |
| GET    | `/movies/search`      | Keyword-based movie search                |
| GET    | `/movies/sort`        | Sort by title, price, duration, or seats  |
| GET    | `/movies/page`        | Paginated movie listing                   |
| GET    | `/movies/browse`      | Combined search + filter + sort + pagination |
| POST   | `/movies`             | Add a new movie                           |
| PUT    | `/movies/{movie_id}`  | Update price or availability              |
| DELETE | `/movies/{movie_id}`  | Remove a movie                            |

---

### Bookings

| Method | Endpoint            | Description                    |
|--------|---------------------|--------------------------------|
| GET    | `/bookings`         | All bookings with revenue total|
| POST   | `/bookings`         | Create a new booking           |
| GET    | `/bookings/active`  | View currently active bookings |
| GET    | `/bookings/search`  | Search by customer name        |
| GET    | `/bookings/sort`    | Sort by cost or seat count     |
| GET    | `/bookings/page`    | Paginated booking list         |

---

### Seat Hold Workflow

| Method | Endpoint                    | Description                        |
|--------|-----------------------------|------------------------------------|
| POST   | `/seat-hold`                | Hold seats temporarily             |
| GET    | `/seat-hold`                | View all active holds              |
| POST   | `/seat-confirm/{hold_id}`   | Confirm hold → create booking      |
| DELETE | `/seat-release/{hold_id}`   | Cancel hold, restore seats         |

---

## Project Structure

```
fastapi-final-project/
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
```

---

## Screenshots

Endpoint outputs are documented in the `screenshots/` folder:

- **Q1–Q5** — Home, Movies, Bookings, Summary
- **Q6–Q7** — Validation errors, Helper functions
- **Q8–Q10** — Booking creation, Promo codes, Filtering
- **Q11–Q13** — Add, Update, Delete movies
- **Q14–Q15** — Seat hold and confirmation flow
- **Q16–Q20** — Search, Sort, Pagination, Browse endpoint

---

## Key Takeaways

Working on this project provided hands-on experience with:
- Designing and structuring RESTful APIs in FastAPI
- Input validation and error handling using Pydantic
- Managing application state with in-memory data stores
- Building multi-step transactional workflows (seat hold → confirm)
- Implementing search, filter, sort, and pagination patterns
- Writing clean, maintainable backend code

---

## Author

**Mohammed Sahil Ahmed**

---

## Acknowledgement

Developed as part of the FastAPI Internship at **Innomatics Research Labs**, February 2026.