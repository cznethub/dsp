### Initial Import of Legacy Resource Instructions

1. Update the `.env` file
2. `chmod +x copy_schema.sh`
3. `./copy_schema.sh`
4. `docker build -t scrapers .`
5. `docker run --env-file ./.env scrapers python earthchem.py`
6. `docker run --env-file ./.env scrapers python hydroshare.py`
7. `docker ps -a | awk '{ print $1,$2 }' | grep scrapers | awk '{print $1 }' | xargs -I {} docker rm {}`
8. `docker rmi $(docker images 'scrapers' -a -q)`
