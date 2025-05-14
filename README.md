# Font Proxy

This project is a Flask application that proxies and caches Google Fonts (CSS and font files) to make them available without tracking.

## Local Execution

1. Ensure you have `uv` installed for dependency management.
2. Initialize the environment (if not already done):

   ```bash
   uv init
   ```

3. Install dependencies:

   ```bash
   uv pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   flask run
   ```

   The application will be available at `http://127.0.0.1:5000`.

## Containerized Execution

1. Build the Docker image:

   ```bash
   docker build -t font-proxy .
   ```

2. Run the application using Docker:

   ```bash
   docker run -p 5000:5000 font-proxy
   ```

Alternatively, you can use `docker-compose`:

1. Start the application:

   ```bash
   docker-compose up
   ```

2. The application will be available at `http://127.0.0.1:5000`.

## Notes

- Ensure that the `pyproject.toml` file is properly configured for dependency management.
- For production deployment, use `gunicorn` as the WSGI server.
