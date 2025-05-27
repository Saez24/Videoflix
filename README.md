# Videoflix (Frontend)

**Description**: Angular frontend for "Videoflix" – a video streaming platform.

## Table of Contents

1. [Features](#features)
2. [Technologies](#technologies)
3. [Setup](#setup)
4. [Development](#development)
5. [Docker Deployment](#docker-deployment)
6. [License](#license)

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
| TypeScript       | Language           |
| RxJS             | State management   |
| Angular Material | UI components      |
| JWT              | Authentication     |
| Docker           | Containerization   |

## Setup

### Prerequisites

- Node.js 18+
- Angular CLI 19+
- Docker (optional)

```bash
# Clone repository
git clone https://github.com/Saez24/Videoflix_Frontend_DA.git
cd Videoflix_Frontend_DA

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
  apiUrl: 'http://your-backend-server:8000/api',
  baseUrl: 'http://your-backend-server:8000',
};

```

environment.ts (production)

```bash

export const environment = {
  production: true,
  apiUrl: 'http://your-backend-server:8000/api',
  baseUrl: 'http://your-backend-server:8000',
};

```

## 👨‍💻 Development

Running the app

```bash

ng serve --open

```

## 🐳 Docker Deployment

Production Build with Docker

```bash

docker-compose up --build

```

📝 License

MIT License © 2023 [Saez24]
Feel free to use, modify, and distribute this project.
