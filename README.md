### Requirements Design for Data Import Quality Assessment Web App

### Overview

The objective is to design a web application that acts as an intermediary for importing data into another application, ensuring the data quality based on predefined rules. The application will support CSV and XLSX file formats and will validate data according to different rules, including regular expressions and length criteria. The backend will be built with FastAPI, and the frontend will eventually be developed using React. Integration with Google's address API for address validation is planned for the long term.

### Functional Requirements

1. **Data Import Formats**
    - Support for importing data in CSV and XLSX formats.
2. **Data Content Variation**
    - Ability to handle different data structures depending on the purpose, such as:
        - Supplier data (including tax IDs and addresses)
        - Contract data (including payment terms and banking information)
        - Rows and columns with non-traditional start coordinates. For example, the header and the first row of data can be several rows apart
3. **Data Validation Rules**
    - Implementation of various data validation rules:
        - Regular expressions for specific field formats
        - Minimum and maximum length criteria
        - Tax ID validation based on country code
        - Username validation (minimum of eight characters)
        - Password validation
4. **Address Validation**
    - Integration with Google's address API for address validation (long-term goal)
5. **Backend API**
    - Development of a backend API using FastAPI to:
        - Ingest CSV and XLSX files
        - Assess data quality based on predefined rules
        - Provide authentication mechanisms
        - Support data streaming
        - Manage data using PostgreSQL
6. **Frontend**
    - Development of a frontend using React (future integration)

### Non-Functional Requirements

1. **Performance**
    - The API should handle large data files efficiently.
    - Data validation should be performed quickly to minimize latency.
2. **Scalability**
    - The system should be able to scale to handle increasing amounts of data and concurrent users.
3. **Security**
    - Ensure secure data transmission and storage.
    - Implement robust authentication and authorization mechanisms.
4. **Usability**
    - The frontend should provide a user-friendly interface for uploading files and viewing validation results.
    - It is important to provide reactive feedback to users due to the potential size of some data sets.
5. **Maintainability**
    - The codebase should be well-documented and follow best practices to facilitate maintenance and future enhancements.

### Technical Specifications

1. **Backend**
    - **Framework**: FastAPI
    - **Database**: PostgreSQL
    - **Authentication**: JWT or OAuth2
    - **Data Streaming**: WebSockets or Server-Sent Events (SSE)
2. **Frontend**
    - **Framework**: React
    - **State Management**: Redux or Context API
3. **Integration**
    - **Address Validation**: Google Address API

### API Endpoints

1. **Authentication**
    - `POST /auth/login`: User login
    - `POST /auth/register`: User registration
2. **Data Import**
    - `POST /data/import`: Upload CSV/XLSX file for validation
3. **Data Validation**
    - `GET /data/validation-rules`: Fetch the list of validation rules
    - `POST /data/validate`: Validate uploaded data based on rules
4. **Address Validation**
    - `POST /data/validate-address`: Validate addresses using Google Address API (future implementation)

### Database Schema

1. **Users**
    - `id`: UUID
    - `username`: String
    - `password`: String (hashed)
    - `email`: String
2. **Validation Rules**
    - `id`: UUID
    - `field_name`: String
    - `rule_type`: Enum (regex, min_length, max_length, etc.)
    - `rule_value`: String or Integer
3. **Imported Data**
    - `id`: UUID
    - `file_name`: String
    - `uploaded_at`: Timestamp
    - `data_content`: LargeBinary
        -`description`: "Stores the imported data in binary format. Note that this change will impact the ability to perform efficient queries and validations directly on the data. Ensure that the application logic is updated to handle binary data appropriately."
4. **Validation Results**
    - `id`: UUID
    - `imported_data_id`: UUID (Foreign Key)
    - `field_name`: String
    - `validation_status`: Enum (valid, invalid)
    - `error_message`: String

### Implementation Plan

1. **Phase 1: Backend Development**
    - Set up FastAPI framework and PostgreSQL database
    - Implement authentication endpoints
    - Develop data import and validation endpoints
    - Define and store validation rules
2. **Phase 2: Frontend Development**
    - Set up React framework
    - Develop file upload interface
    - Display validation results to the user
3. **Phase 3: Address Validation Integration**
    - Integrate with Google Address API
    - Implement address validation endpoint
4. **Phase 4: Testing and Deployment**
    - Conduct unit and integration tests
    - Deploy the application to a cloud service (e.g., AWS, Azure)
5. **Phase 5: Maintenance and Enhancements**
    - Monitor application performance
    - Implement additional features and improvements based on user feedback