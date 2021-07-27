##PyCharm Setup
TODO - look into a settings repository

- clone
- open project in my pycharm
- point Deployment Configuration docker-compose file to docker-compose.yml
- Deploy. Observe all containers build and run.
- Setup python interpreter to the one in `backend` container
- Setup a path mapping in the interpreter from the cloned repo in the backend directory (use absolute path) to the `/app` directory in the container
- Run backend/main.py using pycharm
- Observe the container is deployed
- Setup Default test runner to pytest (Preferences -> Build, Execution, Deployment -> Python integrated Tools)
- Run the tests/test_db::test_the_db in PyCharm to test containerized db connects


