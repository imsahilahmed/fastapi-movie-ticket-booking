from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from math import ceil

app = FastAPI(title="CineStar Booking API")

# =========================================================
# DATA
# =========================================================

movies = [
    {
        "id": 1,
        "title": "Oppenheimer",
        "genre": "Drama",
        "language": "English",
        "duration_mins": 180,
        "ticket_price": 300,
        "seats_available": 40
    },
    {
        "id": 2,
        "title": "Dune: Part Two",
        "genre": "Sci-Fi",
        "language": "English",
        "duration_mins": 166,
        "ticket_price": 320,
        "seats_available": 12
    },
    {
        "id": 3,
        "title": "The Batman",
        "genre": "Action",
        "language": "English",
        "duration_mins": 176,
        "ticket_price": 280,
        "seats_available": 50
    },
    {
        "id": 4,
        "title": "John Wick: Chapter 4",
        "genre": "Action",
        "language": "English",
        "duration_mins": 169,
        "ticket_price": 270,
        "seats_available": 8
    },
    {
        "id": 5,
        "title": "Everything Everywhere All at Once",
        "genre": "Sci-Fi",
        "language": "English",
        "duration_mins": 139,
        "ticket_price": 260,
        "seats_available": 45
    },
    {
        "id": 6,
        "title": "Top Gun: Maverick",
        "genre": "Action",
        "language": "English",
        "duration_mins": 131,
        "ticket_price": 250,
        "seats_available": 60
    },
    {
        "id": 7,
        "title": "Parasite",
        "genre": "Thriller",
        "language": "Korean",
        "duration_mins": 132,
        "ticket_price": 220,
        "seats_available": 25
    },
    {
        "id": 8,
        "title": "RRR",
        "genre": "Action",
        "language": "Telugu",
        "duration_mins": 187,
        "ticket_price": 240,
        "seats_available": 55
    }
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

# =========================================================
# PYDANTIC MODELS
# =========================================================

class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10, max_length=15)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    genre: str = Field(..., min_length=2, max_length=50)
    language: str = Field(..., min_length=2, max_length=50)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

class SeatHoldRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)

# =========================================================
# HELPERS
# =========================================================

def find_movie(movie_id: int):
    for movie in movies:
        if movie["id"] == movie_id:
            return movie
    return None

def find_hold(hold_id: int):
    for hold in holds:
        if hold["hold_id"] == hold_id:
            return hold
    return None

def calculate_ticket_cost(base_price: int, seats: int, seat_type: str, promo_code: str = ""):
    seat_type = seat_type.lower()

    if seat_type == "premium":
        price_per_seat = base_price * 1.5
    elif seat_type == "recliner":
        price_per_seat = base_price * 2
    else:
        price_per_seat = base_price

    original_cost = price_per_seat * seats

    discount_percent = 0
    promo_code = promo_code.upper()

    if promo_code == "SAVE10":
        discount_percent = 10
    elif promo_code == "SAVE20":
        discount_percent = 20

    discount_amount = (original_cost * discount_percent) / 100
    final_cost = original_cost - discount_amount

    return {
        "price_per_seat": price_per_seat,
        "original_cost": round(original_cost, 2),
        "discount_amount": round(discount_amount, 2),
        "discounted_cost": round(final_cost, 2),
        "promo_code_applied": promo_code if promo_code in ["SAVE10", "SAVE20"] else "NONE"
    }

def filter_movies_logic(genre=None, language=None, max_price=None, min_seats=None):
    filtered = movies

    if genre is not None:
        filtered = [movie for movie in filtered if movie["genre"].lower() == genre.lower()]

    if language is not None:
        filtered = [movie for movie in filtered if movie["language"].lower() == language.lower()]

    if max_price is not None:
        filtered = [movie for movie in filtered if movie["ticket_price"] <= max_price]

    if min_seats is not None:
        filtered = [movie for movie in filtered if movie["seats_available"] >= min_seats]

    return filtered

# =========================================================
# DAY 1 - BASIC GET ROUTES
# =========================================================

@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

@app.get("/movies")
def get_movies():
    total_seats_available = sum(movie["seats_available"] for movie in movies)
    return {
        "movies": movies,
        "total": len(movies),
        "total_seats_available": total_seats_available
    }

@app.get("/bookings")
def get_bookings():
    total_revenue = sum(booking["total_cost"] for booking in bookings)
    return {
        "bookings": bookings,
        "total": len(bookings),
        "total_revenue": round(total_revenue, 2)
    }

@app.get("/bookings/active")
def get_active_bookings():
    active = [booking for booking in bookings if booking.get("status", "confirmed") in ["confirmed", "held_confirmed"]]
    return {
        "active_bookings": active,
        "total_active": len(active)
    }

@app.get("/bookings/search")
def search_bookings(customer_name: str):
    matched = [
        booking for booking in bookings
        if customer_name.lower() in booking["customer_name"].lower()
    ]

    return {
        "total_found": len(matched),
        "bookings": matched
    }

@app.get("/bookings/sort")
def sort_bookings(
    sort_by: str = "total_cost",
    order: str = "asc"
):
    allowed_sort_fields = ["total_cost", "seats"]
    allowed_orders = ["asc", "desc"]

    if sort_by not in allowed_sort_fields:
        return {"error": f"Invalid sort_by. Allowed: {allowed_sort_fields}"}

    if order not in allowed_orders:
        return {"error": "Invalid order. Use 'asc' or 'desc'"}

    sorted_bookings = sorted(
        bookings,
        key=lambda x: x[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "bookings": sorted_bookings
    }

@app.get("/bookings/page")
def paginate_bookings(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10)
):
    total = len(bookings)
    total_pages = ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    paginated_bookings = bookings[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "bookings": paginated_bookings
    }

@app.get("/movies/summary")
def movies_summary():
    genre_count = {}
    for movie in movies:
        genre = movie["genre"]
        genre_count[genre] = genre_count.get(genre, 0) + 1

    most_expensive = max(movies, key=lambda x: x["ticket_price"])
    cheapest = min(movies, key=lambda x: x["ticket_price"])
    total_seats = sum(movie["seats_available"] for movie in movies)

    return {
        "total_movies": len(movies),
        "most_expensive_ticket": {
            "title": most_expensive["title"],
            "ticket_price": most_expensive["ticket_price"]
        },
        "cheapest_ticket": {
            "title": cheapest["title"],
            "ticket_price": cheapest["ticket_price"]
        },
        "total_seats_across_movies": total_seats,
        "movies_by_genre": genre_count
    }

@app.get("/movies/filter")
def filter_movies(
    genre: str | None = None,
    language: str | None = None,
    max_price: int | None = None,
    min_seats: int | None = None
):
    filtered = filter_movies_logic(genre, language, max_price, min_seats)
    return {
        "filtered_movies": filtered,
        "count": len(filtered)
    }

@app.get("/movies/search")
def search_movies(keyword: str):
    keyword = keyword.lower()
    matched = [
        movie for movie in movies
        if keyword in movie["title"].lower()
        or keyword in movie["genre"].lower()
        or keyword in movie["language"].lower()
    ]

    if not matched:
        return {
            "message": "No movies found matching your keyword",
            "total_found": 0,
            "movies": []
        }

    return {
        "total_found": len(matched),
        "movies": matched
    }

@app.get("/movies/sort")
def sort_movies(
    sort_by: str = "ticket_price",
    order: str = "asc"
):
    allowed_sort_fields = ["ticket_price", "title", "duration_mins", "seats_available"]
    allowed_orders = ["asc", "desc"]

    if sort_by not in allowed_sort_fields:
        return {"error": f"Invalid sort_by. Allowed: {allowed_sort_fields}"}

    if order not in allowed_orders:
        return {"error": "Invalid order. Use 'asc' or 'desc'"}

    sorted_movies = sorted(
        movies,
        key=lambda x: x[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "movies": sorted_movies
    }

@app.get("/movies/page")
def paginate_movies(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10)
):
    total = len(movies)
    total_pages = ceil(total / limit)
    start = (page - 1) * limit
    paginated_movies = movies[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "movies": paginated_movies
    }

@app.get("/movies/browse")
def browse_movies(
    keyword: str | None = None,
    genre: str | None = None,
    language: str | None = None,
    sort_by: str = "ticket_price",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10)
):
    allowed_sort_fields = ["ticket_price", "title", "duration_mins", "seats_available"]
    allowed_orders = ["asc", "desc"]

    if sort_by not in allowed_sort_fields:
        return {"error": f"Invalid sort_by. Allowed: {allowed_sort_fields}"}

    if order not in allowed_orders:
        return {"error": "Invalid order. Use 'asc' or 'desc'"}

    result = movies

    if keyword is not None:
        kw = keyword.lower()
        result = [
            movie for movie in result
            if kw in movie["title"].lower()
            or kw in movie["genre"].lower()
            or kw in movie["language"].lower()
        ]

    if genre is not None:
        result = [movie for movie in result if movie["genre"].lower() == genre.lower()]

    if language is not None:
        result = [movie for movie in result if movie["language"].lower() == language.lower()]

    result = sorted(
        result,
        key=lambda x: x[sort_by],
        reverse=(order == "desc")
    )

    total = len(result)
    total_pages = ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    paginated = result[start:start + limit]

    return {
        "keyword": keyword,
        "genre": genre,
        "language": language,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "movies": paginated
    }

@app.get("/movies")
def get_movies_alias():
    total_seats_available = sum(movie["seats_available"] for movie in movies)
    return {
        "movies": movies,
        "total": len(movies),
        "total_seats_available": total_seats_available
    }

@app.get("/seat-hold")
def get_seat_holds():
    return {
        "holds": holds,
        "total_holds": len(holds)
    }

@app.get("/movies/{movie_id}")
def get_movie_by_id(movie_id: int):
    movie = find_movie(movie_id)
    if movie:
        return movie
    return {"error": "Movie not found"}

# =========================================================
# DAY 2 + DAY 3 - POST BOOKINGS + HELPERS
# =========================================================

@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    movie = find_movie(request.movie_id)
    if movie is None:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats available"}

    cost_details = calculate_ticket_cost(
        movie["ticket_price"],
        request.seats,
        request.seat_type,
        request.promo_code
    )

    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "movie_id": request.movie_id,
        "movie_title": movie["title"],
        "phone": request.phone,
        "seats": request.seats,
        "seat_type": request.seat_type,
        "promo_code": request.promo_code,
        "original_cost": cost_details["original_cost"],
        "discount_amount": cost_details["discount_amount"],
        "total_cost": cost_details["discounted_cost"],
        "status": "confirmed"
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# =========================================================
# DAY 4 - CRUD
# =========================================================

@app.post("/movies")
def add_movie(new_movie: NewMovie, response: Response):
    for movie in movies:
        if movie["title"].lower() == new_movie.title.lower():
            return {"error": "Movie with this title already exists"}

    new_id = max(movie["id"] for movie in movies) + 1 if movies else 1

    movie_dict = {
        "id": new_id,
        "title": new_movie.title,
        "genre": new_movie.genre,
        "language": new_movie.language,
        "duration_mins": new_movie.duration_mins,
        "ticket_price": new_movie.ticket_price,
        "seats_available": new_movie.seats_available
    }

    movies.append(movie_dict)
    response.status_code = status.HTTP_201_CREATED
    return movie_dict

@app.put("/movies/{movie_id}")
def update_movie(
    movie_id: int,
    ticket_price: int | None = None,
    seats_available: int | None = None
):
    movie = find_movie(movie_id)
    if movie is None:
        return {"error": "Movie not found"}

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price

    if seats_available is not None:
        movie["seats_available"] = seats_available

    return {
        "message": "Movie updated successfully",
        "movie": movie
    }

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if movie is None:
        return {"error": "Movie not found"}

    for booking in bookings:
        if booking["movie_id"] == movie_id:
            return {"error": "Cannot delete movie with existing bookings"}

    movies.remove(movie)
    return {
        "message": "Movie deleted successfully",
        "deleted_movie": movie["title"]
    }

# =========================================================
# DAY 5 - SEAT HOLD WORKFLOW
# =========================================================

@app.post("/seat-hold")
def create_seat_hold(request: SeatHoldRequest):
    global hold_counter

    movie = find_movie(request.movie_id)
    if movie is None:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats available for hold"}

    movie["seats_available"] -= request.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": request.customer_name,
        "movie_id": request.movie_id,
        "movie_title": movie["title"],
        "seats": request.seats,
        "status": "held"
    }

    holds.append(hold)
    hold_counter += 1

    return hold

@app.post("/seat-confirm/{hold_id}")
def confirm_seat_hold(hold_id: int):
    global booking_counter

    hold = find_hold(hold_id)
    if hold is None:
        return {"error": "Hold not found"}

    movie = find_movie(hold["movie_id"])
    if movie is None:
        return {"error": "Movie not found"}

    booking = {
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "movie_id": hold["movie_id"],
        "movie_title": hold["movie_title"],
        "phone": "N/A",
        "seats": hold["seats"],
        "seat_type": "standard",
        "promo_code": "",
        "original_cost": movie["ticket_price"] * hold["seats"],
        "discount_amount": 0,
        "total_cost": movie["ticket_price"] * hold["seats"],
        "status": "held_confirmed"
    }

    bookings.append(booking)
    booking_counter += 1
    holds.remove(hold)

    return {
        "message": "Seat hold confirmed successfully",
        "booking": booking
    }

@app.delete("/seat-release/{hold_id}")
def release_seat_hold(hold_id: int):
    hold = find_hold(hold_id)
    if hold is None:
        return {"error": "Hold not found"}

    movie = find_movie(hold["movie_id"])
    if movie:
        movie["seats_available"] += hold["seats"]

    holds.remove(hold)

    return {
        "message": "Seat hold released successfully",
        "released_hold": hold
    }