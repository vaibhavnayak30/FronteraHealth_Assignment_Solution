# Frontera Health Take Home Assignment

## Overview
Welcome to the solution of "Frontera Health" interview process take home assignment. This application is designed to asynchronously process images to predict whether or not an image has a dog in it or not. 

## Features
- Containerized Deployment
- Asynchronous Image Processing
- Image Classification with YOLOv11
- REST API
    - ```/image_prediction```→ Accepts image input for classification
    - ```/image_prediction/1``` → Image processing status
- Automatic Dependency Management
- Logging & Monitoring
- Simple Setup & Usage
    - Just run ```docker-compose up``` in root directory to bring up the entire application stack

## Prerequisites
Before you start the application, ensure you have the docker and docker-compose setup installed. Follow the steps in the link below to install:
- Docker:
    - https://docs.docker.com/desktop/setup/install/linux/ubuntu/
- Docker-Compose
    - https://docs.docker.com/compose/install/

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/vaibhavnayak30/FronteraHealth_Assignment_Solution.git
    ```
2. Navigate to the project directory:
    ```bash
    cd FronteraHealth_Assignment_Solution
    ```

## Starting the Application
To start the application first time, run the following command:
```bash
docker-compose up --build
```
The application will be available at `http://localhost:8080`.
FAST-API SWAGGER page is available at  `http://localhost:8080/docs`

For subsequent runs, use:
```bash
docker-compose up
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
Submission Details:
- Name: **Vaibhav Nayak** 
- Email: **vaibhavnayak30@gmail.com**
