### Initial Import of Legacy Resource Instructions

1. Update the `.env` file
2. `docker build -t scrapers .`
3. `docker run --env-file ./.env scrapers python earthchem.py`
4. `docker run --env-file ./.env scrapers python hydroshare.py`
5. `docker ps -a | awk '{ print $1,$2 }' | grep scrapers | awk '{print $1 }' | xargs -I {} docker rm {}`
6. `docker rmi $(docker images 'scrapers' -a -q)`
