# Videoflix (backend)

**Description**: This is the backend of my video streaming web application "Videoflix".

## Table of Contents

1. [About the Project](#about-the-project)
2. [Technologies](#technologies)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [API Documentation](#api-documentation)
7. [Testing](#testing)
8. [License](#license)

## About the Project

- This project is a RESTful API backend for a video streaming application https://github.com/Saez24/Videoflix_Frontend_DA
- It allows users to register, verify the account, login, reset the password, request a new password
- Besides that you can upload your own videos with thumbnails, the backend handles the formatting of the thumbnail and the videos
- The videos will afterwards be available in 3 different qualities to stream from (1080p, 720p, 480p) and there will be a video preview when the video is selected on the dashboard

## Technologies

- **Python** 3.13
- **Django** 5.1.4
- **Django REST framework** for building the API
- **RQ** for running complex tasks in the background
- **PostgreSQL** for database management

## Prerequisites

List any software or dependencies that are required to run this project.

- Docker with docker-compose (Docker Desktop)
- Git

## Installation

Step-by-step instructions for setting up the project locally.

1. **Clone the repository**

   ```bash
   git clone https://github.com/Saez24/videoflix_backend.git
   cd videoflix_backend

   ```

2. **Create .env with credentials**

   ```bash
   cp .env.template .env

   ```

5. **Paste credentials with your own values(important) and save the file**

   ```bash"
   DJANGO_SUPERUSER_PASSWORD=adminpassword
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com

   SECRET_KEY="your django secret key"
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200

   DB_NAME=your_database_name,
   DB_USER=your_database_user,
   DB_PASSWORD=your_database_password,
   DB_HOST=db,
   DB_PORT=5432

   REDIS_HOST=redis
   REDIS_LOCATION=redis://redis:6379/1
   REDIS_PORT=6379
   REDIS_DB=0

   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email_user
   EMAIL_HOST_PASSWORD=your_email_user_password
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   DEFAULT_FROM_EMAIL=default_from_email

    ```    

6. **Build and start the project using docker-compose.**

   ```bash"
   docker-compose up --build

   ```
   Open application in browser on `http://localhost:8000/admin`

## Usage

- First of all you need to upload videos in your backend, you need a thumbnail (image in jpg format) and a video (video in mp4 format)
- Visit the admin panel `http://localhost:8000/admin` and log in with your superuser credentials
- Go to the `Content` section and then to `Videos`, give your video a title, description, upload the thumbnail, video and give it a category
- Save your video, the backend will handle the process of converting the video automatically by itself

- After creating a video for your application you can register a new account, verfify it in the email that will be sent, log in to Videoflix and enjoy watching your video!

## API Documentation

This section outlines the main endpoints provided by the API, along with example requests and responses.

**Authentification Endpoints**

- POST `/api/login/`
  Logs a user into the system.

- POST `/api/registration/`
  Registers a user in the system.

- GET `api/registration/verify/<uidb64>/<token>/`
  Verifies the account after registering.

- POST `api/password-reset/request/`
  Sends an e-mail to reset the password.

- GET/POST `api/password-reset/confirm/<uidb64>/<token>/`
  Checks if the password token is valid.

**API CONTENT Endpoints**

Content endpoints provide functionality for managing the video progress of viewed videos and receiving the list of available videos. The following endpoints are available:

- GET `/api/content/videos/`
  Returns a list of all available videos.


## Testing

Instructions for running the automated tests for the project.

1. **Run tests**

Execute all tests:

    python manage.py test

2. **Check test coverage**

get test coverage of the whole application:

    coverage run --source='.' manage.py test
    coverage report -m

## License

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software in accordance with the terms of the MIT License. See the [LICENSE](LICENSE) file for full details.
