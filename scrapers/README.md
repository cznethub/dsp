### Initial Import of Legacy Resource Instructions

1. Update the `.env` file
2. `docker build -t scrapers .`
3. `docker run --env-file ./.env scrapers python earthchem.py`
4. `docker run --env-file ./.env scrapers python hydroshare.py`