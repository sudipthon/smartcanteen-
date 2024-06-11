# Smart Canteen

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/smart-canteen.git
   cd smart-canteen
   ```

2. **Build and Start the Docker Containers**

   docker-compose up -d

3. **Access the Application**

   Open your browser and go to `http://localhost:8000`.

## Services

- **Django**: Available at `http://localhost:8000`
- **RabbitMQ**: Management UI available at `http://localhost:15673` (username: `user`, password: `password`)
- **Celery**: Celery worker logs can be viewed using Docker Compose logs command.

## Viewing Logs

You can view the logs for each service in separate terminals:

- **Django Server Logs**

   docker-compose logs -f web

- **Celery Worker Logs**

   docker-compose logs -f celery

- **RabbitMQ Logs**

   docker-compose logs -f rabbitmq

## Stopping the Containers

To stop the containers, run:

   docker-compose down
