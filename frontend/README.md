# Videoflix (Frontend)

**Description**: Angular frontend for "Videoflix" – a video streaming platform.

## Table of Contents

1. [Features](#features)
2. [Technologies](#technologies)
3. [Setup](#setup)
4. [Development](#development)
5. [Docker Deployment](#docker-deployment)
6. [License](https://github.com/Saez24/Videoflix/blob/main/LICENSE)

## Features

- 🎬 Video streaming with quality selection
- 🔐 User authentication (login/registration)
- 📱 Responsive design
- 🖼️ Video thumbnails and previews
- ⚡ Progressive Web App (PWA) support

## Technologies

| Technology  | Purpose            |
| ----------- | ------------------ |
| Angular 19+ | Frontend framework |
| TypeScript  | Language           |
| Docker      | Containerization   |

## Setup

### Requirements

- [Videoflix Backend](https://github.com/Saez24/Videoflix/tree/main/backend)

### Prerequisites

- Node.js 18+
- Angular CLI 19+
- Docker (optional)

```bash
# Clone repository
git clone https://github.com/Saez24/Videoflix.git
cd Videoflix/frontend


# Install dependencies
npm install

# Start development server
ng serve

```

## Environment Configuration

Create the following files in src/environments/:

environment.development.ts (development)

```bash

export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000/api/',
  staticBaseUrl: 'http://localhost:8000',
};

```

environment.ts (production)

```bash

export const environment = {
  production: true,
  apiBaseUrl: 'http://localhost:8000/api/',
  staticBaseUrl: 'http://localhost:8000',
};

```

## Development

Running the app

```bash

ng serve --open

```

## Docker Deployment

Production Build with Docker

```bash

docker-compose up --build

```

Open application in browser on `http://localhost:8000/admin` and upload your videos.

Open application in browser on `http://localhost`
