🛒 Online Imtiaz Mart API

The Online Imtiaz Mart API is an advanced, event-driven microservices architecture designed to power an online shopping platform. It offers a robust, scalable, and maintainable backend solution for e-commerce, leveraging modern technologies such as FastAPI, Kafka, Docker, Kong, and Protobuf. This API ensures seamless communication between services, efficient order processing, and smooth payment handling.

🎯 Microservices Overview

📦 Product Service:

Handles product listings, details, and inventory updates.
Manages CRUD operations and ensures product availability in real-time.

🛍️ Order Service:

Manages order creation, tracking, and updates.
Interacts with the Product and Inventory Services to verify stock and order details.

🗃️ Inventory Service:

Tracks product stock levels and synchronizes with the Order and Product Services.
Ensures real-time inventory updates and alerts for low stock.

🧑‍💻 User Service:

Manages user registration, authentication, and profile updates.
Provides secure access and interacts with other services for user authentication.

💬 Notification Service:

Sends email and SMS notifications for order statuses, user activities, and payments using Mailjet.
Listens to events from other services via Kafka for real-time notifications.

💰 Payment Service:

Processes payments using PayFast (local) and Stripe (international).
Manages payment intents, confirmations, and integrates with the Notification Service for payment alerts.

📡 Inter-Service Communication

Utilizes Kafka for event-driven communication, ensuring reliable data sharing between services.
Services produce and consume Kafka messages for events like order creation, payment processing, and notifications.

🛠️ Technology Stack

Framework: FastAPI
Messaging: Apache Kafka
Database: PostgreSQL with SQLAlchemy and SQLModel
API Gateway: Kong
Containerization: Docker & Docker Compose
Serialization: Protocol Buffers (Protobuf)
Email Service: Mailjet

🚀 Key Features

Microservices Architecture: Independent, self-contained services for User, Product, Order, Inventory, Notification, and Payment.
Event-Driven Design: Real-time communication between services using Kafka, ensuring responsiveness and scalability.
Secure Payment Processing: Integration with PayFast and Stripe for seamless transaction handling.
Scalability & Flexibility: Dockerized setup ensures easy deployment, scaling, and management of services.
Notifications: Real-time email/SMS notifications for various events, ensuring users are always informed.

🔐 Security & API Management

Kong Gateway is used to manage API traffic, providing security, rate-limiting, and access control to the services.

🌐 How to Get Started

Clone the repository and set up your environment with Docker and Docker Compose.
Use the provided docker-compose.yml to spin up all services and Kafka for inter-service communication.
Refer to the individual service documentation for API endpoints and functionality.