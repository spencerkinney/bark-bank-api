# Bark Banking API

<img src="./bark.png" alt="Bark Bank Logo" width="200"/>

A robust Django-based API for managing bank operations.

## Overview

The Bark API provides comprehensive banking features including account creation, fund transfers, balance inquiries, and transfer history. It is designed to be clean, intuitive, and secure.

## Getting Started

1. **Clone the Repo:**

    ```bash
    git clone https://github.com/spencerkinney/bark-bank-api.git
    cd bark-bank-api
    ```

2. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run Migrations:**

    ```bash
    python manage.py migrate
    ```

4. **Create a Superuser:**

    ```bash
    python manage.py createsuperuser
    ```

5. **Start the Server:**

    ```bash
    python manage.py runserver
    ```

6. **View API Documentation:**
   
   Open your browser and go to `http://localhost:8000/` to view the Swagger UI documentation.
   Alternatively, visit `http://localhost:8000/redoc/` for the ReDoc view.

## API Endpoints

- **List/Create Accounts:** `GET/POST /api/accounts/`
- **Retrieve/Update/Delete Account:** `GET/PUT/PATCH/DELETE /api/accounts/{account_id}/`
- **Get Account Balance:** `GET /api/accounts/{account_id}/balance/`
- **Get Account Transfer History:** `GET /api/accounts/{account_id}/transfers/`
- **List/Create Transfers:** `GET/POST /api/transfers/`
- **Retrieve Transfer Details:** `GET /api/transfers/{transfer_id}/`

## Authentication

This API uses token authentication. To obtain a token, send a POST request to `/token/` with your username and password.

Include the token in the Authorization header of your requests:

```
Authorization: Token your_token_here
```

## Error Handling

The API returns appropriate HTTP status codes and error messages for various scenarios, including:

- 400 Bad Request: For invalid input data
- 401 Unauthorized: For authentication failures
- 403 Forbidden: For permission issues
- 404 Not Found: For non-existent resources
- 500 Internal Server Error: For server-side issues

## Security Considerations

- All monetary transactions are wrapped in database transactions to ensure data integrity.
- Proper permissions are implemented to ensure users can only access and modify their own accounts.
- Input validation is performed on all user inputs to prevent invalid or malicious data.

## Future Enhancements

- Implement rate limiting to prevent abuse
- Add comprehensive logging for all transactions
- Implement multi-factor authentication for sensitive operations

---

*Bark Technologies is a financial technology company, not a bank*