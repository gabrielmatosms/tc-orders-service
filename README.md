### Microserviço dos pedidos - Tech Challenge Fase 4

# Service to take care of the orders

This project is a backend application designed to manage orders and facilitate efficient customer service as the business expands. Using **FastAPI** with a **hexagonal architecture**, the application allows customers to place and track orders and allows administrators to manage products, customers, and orders. It’s built as a monolithic application with a **PostgreSQL** database, containerized for easy deployment using **Docker** and **Docker Compose**.

## Architecture

This project follows a **hexagonal architecture** (also known as ports and adapters), with a clear separation of concerns:

- **Core**: Contains domain models and interfaces.
- **Application**: Contains use cases for business logic.
- **Adapters**: Handles API and database interaction.

## Setup and Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/gabrielmatosms/tc-orders-service.git
   cd tc-payments-service
   ```

2. **Install Docker and Docker Compose** if you haven’t already:

   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

3. **Build and run the application** using Docker Compose:

   ```bash
   docker-compose up --build -d
   ```

## API Endpoints

(Local) The FastAPI Swagger UI is available at: [http://localhost:8009/docs](http://localhost:8009/docs)

## Workflow Representations

### VIDEOS EXPLICATIVOS
Video explicando a arquitetura dos microserviços - [https://www.youtube.com/watch?v=lWntA32xC7I](https://www.youtube.com/watch?v=lWntA32xC7I) - Fase 4
Video mostrando o funcionamento da pipeline - [https://www.youtube.com/watch?v=j2fGOKqMIqY](https://youtu.be/j2fGOKqMIqY) - Fase 4

### Arquitetura dos microserviços
** Acesse o [miro](https://miro.com/app/board/uXjVIy2LsaY=/)
![Diagram de Micro-Servicos](https://github.com/user-attachments/assets/0ea2dc40-3047-4001-88b7-61858c7c9bc9)

### Cobertura de testes
<img width="766" alt="image" src="https://github.com/user-attachments/assets/6984af88-10b2-43f7-9d79-425093a41d97" />

### Pipeline CI/CD
![Untitled-2025-05-18-2204](https://github.com/user-attachments/assets/3b2b7ba2-6504-49ae-83b8-693eaae97ac8)
