# Intellikit Backend Development Manual

## Project Overview
Intellikit is a web application designed to act as an intermediary for importing data into another application, ensuring data quality based on predefined rules. The backend is built using FastAPI, a modern, fast, and efficient web framework for Python.

## Core Functionalities
The Intellikit backend provides the following core functionalities:

### Data Import
- Supports importing data in CSV and XLSX formats.
- Handles various data structures, including supplier data, contract data, and data with non-traditional row and column coordinates.
- Stores imported data in the database in binary format for efficient storage and retrieval.
- Provides an endpoint (POST /api/v1/validator/import/) for uploading and processing files.
- The `import_data` function in `app/validator/service.py` is responsible for handling the file upload and data import logic.

### Data Validation
- Implements various data validation rules, including regular expressions, length criteria, tax ID validation, username validation, and password validation.
- Provides a mechanism to define and store validation rules in the database.
- Performs data validation based on the defined rules and generates validation results.
- Exposes an endpoint (POST /api/v1/validator/validate/) for validating imported data.
- The `validate_data` function in `app/validator/service.py` handles the validation logic and stores the results in the database.

### Authentication
- Implements authentication mechanisms using JWT (JSON Web Token) for secure user access.
- Provides endpoints for user registration (POST /api/v1/auth/users/) and login (POST /api/v1/auth/jwt/login).
- Enforces authorization based on user roles and permissions.
- The authentication-related logic is implemented in the `app/auth` module, with the main router defined in `app/auth/router.py`.

### Data Management
- Utilizes PostgreSQL as the database for storing user data, validation rules, imported data, and validation results.
- Implements data persistence and retrieval using SQLAlchemy.
- The database models are defined in `app/models.py`, and the database connection and session management are handled in `app/database.py`.

## Backend Architecture
The Intellikit backend is structured as follows:

### Entry Point: `app/main.py`
This file is the main entry point for the FastAPI application. It initializes the FastAPI instance, includes routers for different functionalities, and defines the root endpoint.

### Configuration: `app/config.py`
This module defines the application's configuration settings using Pydantic's BaseSettings. It includes settings related to the database, API version prefix, security, and other application-specific configurations.

### Database: `app/database.py`
This module sets up an asynchronous database connection using SQLAlchemy with asyncio support. It configures the database URL, creates an asynchronous engine, and provides a session factory for managing database sessions.

### Models: `app/models.py`
This module defines the SQLAlchemy models for representing database tables, including User, Role, Permission, Group, ImportedData, and ValidationResult.

### Routers: `app/auth/router.py` and `app/validator/router.py`
These modules define the FastAPI routers for handling authentication and validation-related endpoints. The `app/auth/router.py` file includes endpoints for user management, role/permission management, and authentication (login, logout). The `app/validator/router.py` file includes endpoints for data import, data validation, and validation result management.

### Services: `app/auth/service.py` and `app/validator/service.py`
These modules contain the business logic for handling authentication and validation-related operations. The `app/auth/service.py` file includes functions for creating, updating, and deleting users, as well as managing roles and permissions. The `app/validator/service.py` file includes functions for importing data, validating data, and managing validation results.

### Utilities: `app/validator/utils.py`
This module contains utility functions for performing various data validation checks, such as minimum length, maximum length, regular expression matching, and email/country code validation. These functions are used by the `validate_data` function in the `app/validator/service.py` module.

### Exceptions: `app/auth/exceptions.py`
This module defines custom exceptions for handling authentication-related errors, such as invalid credentials, inactive users, and permission denials. These exceptions are used throughout the `app/auth` module to provide meaningful error messages and HTTP status codes.

### Dependencies: `app/auth/dependencies.py`
This module defines the dependencies used for authentication, such as the OAuth2 scheme and functions for creating, decoding, and retrieving the current user from the JWT token. These dependencies are used in the `app/auth/router.py` module to handle authentication-related endpoints.

## Development Workflow
1. **Set up the development environment:**
   - Ensure you have Python 3.11 or higher installed.
   - Install Poetry, the dependency management tool, and use it to install the project dependencies.
   - Set up the PostgreSQL database and update the DATABASE_URL in the .env file.

2. **Run the application:**
   - Use the `run_app.py` script to start the FastAPI application in development mode. The application will be available at `http://localhost:8000/api`.

3. **Implement new features or fix bugs:**
   - Identify the relevant module(s) and file(s) where the changes need to be made.
   - Implement the new functionality or fix the bug, following the existing code structure and design patterns.
   - Add unit tests for the new functionality or bug fix to ensure the changes work as expected.

4. **Update the documentation:**
   - Ensure the README.md file is up-to-date with any changes to the project's requirements, technical specifications, or implementation details.
   - Update the docstrings and comments in the code to reflect the changes made.

5. **Run tests and linting:**
   - Use the provided pytest and ruff commands to run the test suite and check for code style issues.
   - Fix any issues identified during the testing and linting process.

6. **Deploy the changes:**
   - Once the changes have been thoroughly tested and documented, create a new branch and submit a pull request for review.
   - After the pull request is approved and merged, deploy the changes to the production environment.

## Best Practices
- Follow the existing code structure and design patterns to maintain consistency throughout the codebase.
- Write clear and concise docstrings for all functions, classes, and modules to improve code readability and maintainability.
- Implement comprehensive unit tests to ensure the reliability and stability of the backend.
- Adhere to the PEP8 style guide and use tools like ruff to maintain code quality.
- Regularly review and update the project's documentation to keep it accurate and up-to-date.
- Continuously monitor the application's performance and scalability, and make necessary optimizations as the project grows.

## FastAPI Documentation References
The Intellikit backend leverages several features and concepts from the FastAPI framework. Here are some relevant sections from the FastAPI documentation that may be helpful during development:
- **FastAPI Tutorial - User Guide:** This section covers the basics of creating FastAPI applications, including path operations, request and response models, and data validation.
- **FastAPI Advanced User Guide:** This section delves into more advanced topics, such as custom responses, middleware, and WebSockets.
- **FastAPI Reference - Code API:** This section provides detailed documentation on the various classes and functions available in the FastAPI framework.

By leveraging the comprehensive documentation and following the best practices outlined in this manual, you can effectively maintain and enhance the Intellikit backend codebase.