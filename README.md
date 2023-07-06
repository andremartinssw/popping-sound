## Usage

### Build the container:
`docker build . -t popping`

### Run the container
**Linux**\
`docker run --net=host -it -v $(pwd)/recordings:/app/recordings --rm --name popping --env-file .env popping`

**MacOS/Windows (I haven't tested this, let me know if it does not work)**  
`docker run -it -v $(pwd)/recordings:/app/recordings --rm --name popping --env-file .env popping host.docker.internal:5000`