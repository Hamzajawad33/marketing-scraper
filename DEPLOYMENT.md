# Deployment Guide

This application is containerized using Docker, which makes it easy to deploy to platforms like **Render**, **Railway**, or any VPS.

## Recommended: Deploy to Render.com (Free/Cheap)

Render is excellent for this because it supports Docker natively.

1.  **Push your code to GitHub**:
    - Make sure this project is in a GitHub repository.

2.  **Create a New Web Service on Render**:
    - Go to [dashboard.render.com](https://dashboard.render.com).
    - Click **New +** -> **Web Service**.
    - Connect your GitHub repository.

3.  **Configure the Service**:
    - **Name**: `marketing-scraper` (or whatever you like)
    - **Runtime**: Select **Docker** (Important!)
    - **Region**: Choose one close to you.
    - **Instance Type**: Free (might be slow for scraping) or Starter ($7/mo).

4.  **Environment Variables**:
    - Scroll down to "Environment Variables" and add:
        - `SECRET_KEY`: (Generate a random string)
        - `FLASK_DEBUG`: `False`
        - `PORT`: `5000`

5.  **Deploy**:
    - Click **Create Web Service**.
    - Render will build the Docker image (this takes a few minutes because it installs Chrome).

## Option 2: Run Locally with Docker

If you have Docker Desktop installed, you can run the production version locally:

1.  **Build the Image**:
    ```bash
    docker build -t marketing-scraper .
    ```

2.  **Run the Container**:
    ```bash
    docker run -p 5000:5000 -e SECRET_KEY=mysecret -e FLASK_DEBUG=False marketing-scraper
    ```

3.  **Access**:
    - Go to `http://localhost:5000`.

## Troubleshooting

-   **Memory Issues**: Chrome uses a lot of RAM. If the scraper crashes on the Free tier, try upgrading to a paid instance with more RAM.
-   **Timeouts**: Scraping takes time. Ensure your platform's timeout settings (usually 30s-60s for web requests) don't kill the connection. The scraper runs in a background thread, so the web request returns immediately, which is good design!
