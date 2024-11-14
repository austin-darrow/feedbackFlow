## About this app
This application will provide AI-powered formative writing feedback to teachers on their student's writing.


## Instructions for use
- Clone the repo
- Add a .env with the following keys to the root of the project directory:
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - NVIDIA_API_KEY (generate one here: https://build.nvidia.com/nvidia/llama-3_1-nemotron-70b-instruct)
    - JWT_SECRET_KEY
    - TEST_EMAIL
    - TEST_PASSWORD
- Ensure you have Docker installed
- Type 'make run' in the command line to start the backend app