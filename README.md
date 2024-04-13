# Data Pusher

Data Pusher is a Python application designed to receive JSON data and send it across different platforms (destinations) from specific accounts using webhook URLs.

## Overview

Data Pusher is a versatile tool for handling data transmission needs. It offers modules for managing accounts, destinations, and data handling, along with APIs for CRUD operations and data reception. This README provides an overview of the project structure, functionalities, and instructions for setting up and running the application.

## Features

- **Account Management**: Create, read, update, and delete accounts.
- **Destination Management**: Manage destinations for each account.
- **Data Handling**: Receive JSON data and send it to designated destinations based on account settings.
- **Security**: Authentication through App Secret Token ensures data integrity.
- **FastAPI Web Application**: Utilizes FastAPI for efficient web application development.

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
```

2. Navigate to the project directory:

```bash
cd data-pusher
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the FastAPI web application:

```bash
uvicorn main:app --reload
```

2. Access the API documentation:

Open your web browser and go to `http://localhost:8000/docs`.

3. Use the provided endpoints for managing accounts, destinations, and receiving data.

## API Endpoints

- **Account Endpoints**:

  - `GET /accounts`: Retrieve all accounts.
  - `GET /accounts/{account_id}`: Retrieve details of a specific account.
  - `POST /accounts`: Create a new account.
  - `PUT /accounts/{account_id}`: Update an existing account.
  - `DELETE /accounts/{account_id}`: Delete an account.

- **Destination Endpoints**:

  - `GET /accounts/{account_id}/destinations`: Retrieve all destinations for a specific account.
  - `GET /accounts/{account_id}/destinations/{destination_id}`: Retrieve details of a specific destination.
  - `POST /accounts/{account_id}/destinations`: Create a new destination for an account.
  - `PUT /accounts/{account_id}/destinations/{destination_id}`: Update an existing destination.
  - `DELETE /accounts/{account_id}/destinations/{destination_id}`: Delete a destination.

- **Data Reception Endpoint**:
  - `POST /server/incoming_data`: Receive JSON data and send it to destinations based on account settings.
