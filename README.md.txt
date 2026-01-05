Bluestock ML Financial Analysis Dashboard

A full‑stack fintech project that fetches real stock fundamentals from Bluestock’s API, applies rule‑based ML‑style analysis, stores results in a database, and displays insights on a React dashboard.

1. Architecture Overview
Backend: Django + Django REST Framework

  * Connects to Bluestock company API    (company.php?id={company_id}&api_key=...).

  * Cleans and aggregates financial data and official pros/cons.

  * Applies rule‑based analyzer to classify companies as GOOD / NEUTRAL / BAD.

  * Stores results in PostgreSQL and exposes REST endpoints.

Database: PostgreSQL

  * Company table: basic info + selected financial metrics.

  * Analysis table: health rating, combined pros/cons, timestamp.

Frontend: React + Axios

  * Single‑page dashboard for entering company symbols (Nifty100).

  * Calls backend APIs and renders cards with Bluestock metrics + ML insights.

2. Tech Stack

  * Python 3.11

  * Django 4.2, Django REST Framework

  * PostgreSQL

  * Requests, python‑dotenv

  * React (create‑react‑app), Axios, CSS

3. Backend Setup (Django + PostgreSQL)

3.1 Clone and enter project
bash
git clone <your-repo-url> bluestock-ml-project
cd bluestock-ml-project/backend

3.2 Create and activate virtualenv
bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

3.3 Install dependencies
bash
pip install -r requirements.txt
(If requirements.txt not yet generated, use pip freeze > requirements.txt after installing packages.)

3.4 Configure PostgreSQL
Create database and user:

sql
CREATE DATABASE bluestock_db;
CREATE ROLE bluestock_user WITH LOGIN PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bluestock_db TO bluestock_user;

In bluestock_config/settings.py:

python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "bluestock_db",
        "USER": "bluestock_user",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

3.5 Environment variables
Create .env in backend/:

text
API_KEY=your_bluestock_api_key
(Optionally DB credentials too if you want.)

3.6 Migrations and runserver
bash
python manage.py migrate
python manage.py runserver

Backend runs at http://127.0.0.1:8000/.

4. Frontend Setup (React)
From project root:

bash
cd frontend
npm install
npm start

Frontend runs at http://localhost:3000/.

5. API Endpoints

5.1 Analyze companies
URL: POST /api/analyze/?format=json

Body (JSON):

json
{
  "company_ids": ["TCS", "HDFCBANK", "INFY"]
}
Response (simplified):

json
{
  "status": "success",
  "count": 3,
  "results": [
    {
      "company_id": "TCS",
      "company_name": "Tata Consultancy Services Ltd",
      "health_rating": "NEUTRAL",
      "pros": ["Company is almost debt free.", "..."],
      "cons": ["Stock is trading at 15.2 times its book value", "..."],
      "metrics_summary": {
        "sales_growth_10y": "10 Years: 11%",
        "roe_10y": "10 Years: 40%"
      },
      "details_url": "https://bluemutualfund.in/app1/pages/company.php?id=TCS"
    }
  ]
}

5.2 List stored analyses
URL: GET /api/results/?format=json

Description: Returns all companies stored in the Analysis table along with their latest health rating and pros/cons.

6. How the Analysis Works
Fetch data:

  * Backend calls Bluestock API for each requested company_id.

  * Parses:

    * company (name, ROE, etc.)

    * data.prosandcons (official pros/cons text)

data.analysis (10Y / 5Y / 3Y growth & ROE).

Preprocess / clean:

Normalize IDs to uppercase.

Convert numeric strings to numbers where needed.

Remove "NULL" entries from pros/cons.

Rule‑based analyzer:

Uses ROE, debt, growth and dividend indicators (when available) to generate additional pros/cons and a GOOD / NEUTRAL / BAD health rating.

Combine & store:

Merges Bluestock pros/cons with ML pros/cons.

Saves Company + Analysis records into PostgreSQL.

Return to frontend:

React receives results[] and renders cards.

7. Frontend Features
Search bar to enter company symbols (e.g., TCS, HDFCBANK, INFY).

Chip list to add/remove symbols dynamically.

Analyze button to call backend API.

Result cards per company showing:

Company name and health badge (GOOD / NEUTRAL / BAD).

Bluestock 10Y Sales and 10Y ROE metrics.

Detailed Pros and Cons lists.

“View full Bluestock analysis →” link opening the official Bluestock page.

Filter bar: ALL / GOOD / NEUTRAL / BAD to quickly segment companies.

8. Testing

8.1 API testing (Postman)
Create requests for:

POST /api/analyze/ with valid/invalid bodies.

GET /api/results/.

Verify:

HTTP 200 with correct JSON on success.

HTTP 400 when company_ids is missing or invalid.

8.2 UI testing
Test with various symbol sets:

Single company, many companies, duplicates, invalid ticker.

Check:

Cards render correctly, no crashes.

Filters work.

Error banner appears if backend is down.

9. Environment Templates
Create .env.example in backend:

text
API_KEY=your_bluestock_api_key
DB_NAME=bluestock_db
DB_USER=bluestock_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432

