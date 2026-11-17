# Smart Tourism Intelligence and Personalized Destination Recommendation System

MCA I Mini Project, Kamala Education Society's Pratibha Institute of Business Management (PIBM), Chinchwad, Pune (2026-2028).

**Student:** Neha Gatti  
**Guide:** Prof. Ashwini Joshi

A web-based decision-support application that helps travellers choose a destination in Maharashtra according to their budget, available days, interests and travel month, then estimate the trip cost and save a day-wise itinerary.

## Features

- User registration, login and logout (passwords stored as hashes)
- Destination list with search and category filter
- Personalized recommendations: filter, score (0-100) and rank, with the reasons shown
- Destination comparison (2-4 destinations side by side)
- Budget estimation: transport, stay, food, activities, total and per-person cost
- Day-wise itinerary: save, view, edit and delete trips
- Ratings and reviews (one review per user per destination)
- Admin dashboard with Chart.js charts (staff only)
- Destination management through the Django admin panel

## How the recommendation works

1. **Filter:** remove destinations that need more days than the user has, cost more than the budget, or are outside the chosen interests.
2. **Score** each remaining destination out of 100:

| Factor | Weight |
|---|---|
| Interest match | 40% |
| Budget suitability | 30% |
| Duration suitability | 15% |
| Seasonal suitability | 15% |

3. **Rank** by score (cheaper destination wins a tie) and show the reasons.

## Technology

Python 3.13, Django 5.2 LTS, MySQL 8.0, HTML, CSS, JavaScript, Bootstrap 5, Chart.js, VS Code, MySQL Workbench, Git and GitHub.

## Setup

1. Clone the repository and open the folder:
   ```
   git clone https://github.com/[your-username]/smart-tourism.git
   cd smart-tourism
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
4. In MySQL Workbench create the database and user:
   ```sql
   CREATE DATABASE smart_tourism CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'tourism_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON smart_tourism.* TO 'tourism_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
5. Copy `.env.example` to `.env` and enter your password.
6. Build the tables, load sample data and create an admin:
   ```
   python manage.py migrate
   python manage.py seed_data
   python manage.py createsuperuser
   ```
7. Start the server and open http://127.0.0.1:8000
   ```
   python manage.py runserver
   ```

If there is no `.env` file, the project falls back to SQLite.

## Scope and limitations

- Covers 16 selected Maharashtra destinations from a curated dataset.
- All costs are **estimates**, not live prices.
- It does not book hotels or transport, process payments, or use live maps or weather.
- Popularity forecasting is not included, because no suitable historical dataset was available. It is listed as future scope.

## Future scope

Live map, weather and transport APIs, route ordering, more destinations across India, forecasting with historical data, collaborative filtering, a mobile app, multilingual support and PDF export of itineraries.

## Screenshots

[Add 4-5 screenshots later: home page, recommendation results, trip plan, comparison, dashboard]