## About this app
This application will provide AI-powered formative writing feedback to teachers on their student's writing.


## Instructions for use
- Clone the repo
- Add a .env with the following keys to the root of the project directory:
    - NVIDIA_API_KEY (generate one here: https://build.nvidia.com/nvidia/llama-3_1-nemotron-70b-instruct) if using NVIDIA model
    - GITHUB_API_KEY (generate on github)
    - JWT_SECRET_KEY
    - MODEL (name of model--llama/nvidia)
- Push to Heroku to deploy