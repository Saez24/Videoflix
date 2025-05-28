# Videoflix

Angular frontend and Django backend for "Videoflix" – a video streaming platform.

## Table of Contents

1. [Features](#features)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Usage](#usage)
5. [License](https://github.com/Saez24/Videoflix/blob/main/LICENSE)

## Features

- 🎬 Video streaming with quality selection
- 🔐 User authentication (login/registration)
- 📱 Responsive design
- 🖼️ Video thumbnails and previews
- ⚡ Progressive Web App (PWA) support

## Technologies

| Technology       | Purpose            |
| ---------------- | ------------------ |
| Angular 19+      | Frontend framework |
| Django 5+        | Backend framework  |
| TypeScript       | Language           |
| Python           | Language           |
| RxJS             | State management   |
| Angular Material | UI components      |
| Postgres         | Database           |
| Redis            | Database           |
| Docker           | Containerization   |

This project is structured as a monorepo using Git submodules.  
It consists of two main components:

- [Frontend](https://github.com/Saez24/Videoflix/tree/main/frontend)
- [Backend](https://github.com/Saez24/Videoflix/tree/main/backend)

Both components are included as Git submodules.

## Installation

1. Clone this repository along with its submodules, use:

```bash

git clone https://github.com/Saez24/Videoflix.git
cd Videoflix

```

2. **Create environments with credentials**

Backend
.env

```bash
cp backend/.env.template backend/.env

```

Frontend
environment.development.ts (development)
environment.ts (production)

```bash

cp frontend/src/environments/environment.template.ts frontend/src/environments/environment.ts
cp frontend/src/environments/environment.development.template.ts frontend/src/environments/environment.development.ts 

```

3. **Paste credentials with your own values(important) and save the file**

Banend .env

```bash"
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com

SECRET_KEY="your django secret key"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1

FRONTEND_URL=http://localhost

DB_NAME=your_database_name,
DB_USER=your_database_user,
DB_PASSWORD=your_database_password,
DB_HOST=db,
DB_PORT=5432

POSTGRES_USER=${DB_USER}
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=${DB_NAME}
POSTGRES_HOST=${DB_HOST}
POSTGRES_PORT=${DB_PORT}

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=1

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=default_from_email

```

Frontend environment.ts & environment.development.ts

```bash

apiBaseUrl: 'http://localhost:8000/api/',
staticBaseUrl: 'http://localhost:8000',

```


4. **Build and start the project using docker-compose.**

```bash"
docker-compose up --build
```

Open application in browser on `http://localhost`

## Usage

- First of all you need to upload videos in your backend, you need a thumbnail (image in jpg format) and a video (video in mp4 format)
- Visit the admin panel `http://localhost:8000/admin` and log in with your superuser credentials
- Go to the `Content` section and then to `Videos`, give your video a title, description, upload the thumbnail, video and give it a category
- Save your video, the backend will handle the process of converting the video automatically by itself

- After creating a video for your application you can register a new account, verfify it in the email that will be sent, log in to Videoflix and enjoy watching your video!
