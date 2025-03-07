# Health Management System (Projeto de Bases de Dados 2023/2024)

## Project Overview

The **Health Management System** is a web-based application designed to manage clinics, doctors, patients, and consultations. It facilitates the process of managing health-related appointments, handling medical records, and integrating various databases for a healthcare environment. This project was developed as part of the **Projeto de Bases de Dados** for the 2023/2024 academic year.

The application uses a **PostgreSQL** database to store data and provides a **RESTful API** for interacting with the database. The application includes functionality for registering, canceling, and listing consultations, managing clinics, specialties, and doctors, as well as integrating patient data and prescriptions.

## Team Members
- **Tiago Branquinho** (GitHub: [tsbranquinho](https://github.com/tsbranquinho))
- **Rafael Avelar** (GitHub: [RafaelAvelar14](https://github.com/RafaelAvelar14))
- **Lara Faria** (Github: [lara-gfaria](https://github.com/lara-gfaria))

## Key Features

- **Clinics Management**: Listing clinics with their name, address, and phone number.
- **Doctor and Specialties Management**: Ability to list specialties available at clinics, along with available doctors and their consultation times.
- **Consultation Management**: Register, cancel, and view consultations, ensuring all rules for scheduling and canceling are enforced.
- **Patient Management**: Support for registering patient data, managing consultations, and recording medical prescriptions and observations.
- **Web API**: Provides a REST API that allows interaction with the system for consultation management, registration, and data retrieval.

## Repository Contents

- **`app.py`**: Main Flask application to serve the REST API for managing consultations, clinics, doctors, and patients.
- **`write_sql_database.py`**: Script to populate the database with synthetic data for testing and demonstration purposes, including random generation of medical records.
- **SQL Scripts**:
  - **`analise_de_dados.sql`**: Contains SQL queries for data analysis.
  - **`indices.sql`**: Defines SQL queries for creating necessary indices to improve performance.
  - **`populate.sql`**: Contains SQL commands for populating the database with essential data.
  - **`restricoes.sql`**: SQL commands for adding integrity constraints in the database.
  - **`saude.sql`**: The SQL schema for creating the healthcare database and tables.
  - **`test.sql`**: Sample queries for testing and validating the data and queries.
  - **`vistas.sql`**: SQL views for combining important data from multiple tables.
- **`README.md`**: This file, providing an overview of the project.

## How It Works

The system leverages **PostgreSQL** as the database backend, using a series of SQL scripts to create the database schema, populate tables with sample data, and perform analytical tasks. The **Flask application** (`app.py`) is responsible for serving the REST API, allowing external applications or services to interact with the system.

### Key Components:
1. **Web Service**: Exposes several endpoints to manage clinics, doctors, specialties, consultations, and patients.
2. **Database**: The database stores all relevant health data, including clinic details, medical records, consultation times, and patient information.
3. **Data Population Script**: The `write_sql_database.py` script generates mock data for the database using random generation techniques.
4. **SQL Scripts**: Multiple SQL files are provided for creating the database schema, populating tables, creating indices, and executing specific queries.

## Usage

### Running the Flask Application

1. **Install Dependencies**:
   To install the necessary dependencies, use:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Flask App**:
   To run the Flask application, execute the following:
   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000` by default.

3. **Using the API**:
   The following are the key endpoints available in the API:

   - **`GET /`**: List all clinics with their name and address.
   - **`GET /c/<clinica>/`**: List all specialties offered at a specific clinic.
   - **`GET /c/<clinica>/<especialidade>/`**: List all doctors in a specific specialty at a clinic and their next available consultation times.
   - **`POST /a/<clinica>/registar/`**: Register a new consultation at a clinic.
   - **`DELETE /a/<clinica>/cancelar/`**: Cancel a consultation.

4. **Populating the Database**:
   To populate the database with synthetic data, run the following script:
   ```bash
   python write_sql_database.py
   ```

   This will generate a `data.sql` file that contains all necessary SQL commands to populate the database.

### SQL Scripts

- **Creating the Database**: The `saude.sql` script defines the schema for the database, including all necessary tables.
- **Inserting Data**: The `populate.sql` script can be used to populate the database with a set of test data.
- **Running Queries**: The `analise_de_dados.sql` script contains various queries for analyzing patient data, prescriptions, and consultations.
- **Creating Indexes**: The `indices.sql` script defines the indexes for optimizing query performance.

## Conclusion

This project provides a comprehensive solution for managing health-related data through a web API, demonstrating the application of database management, web development, and integration of SQL for data analysis and performance optimization.

---
