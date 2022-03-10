## Building Docker image

Start by locking dependencies (if necessary):

    pipenv lock -r > requirements.txt

Then build the Docker image:

    docker build -t meteringpoints:v1 .
    

## Running container images

API:

    docker run --entrypoint /app/entrypoint_api.sh meteringpoints:v1

Consumer:

    docker run --entrypoint /app/entrypoint_consumer.sh meteringpoints:v1