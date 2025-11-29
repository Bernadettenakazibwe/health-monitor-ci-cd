# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Install system dependencies (optional but safe for many Python deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first (for better build caching)
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose port 5000 (same as Flask/Gunicorn)
EXPOSE 5000

# 8. Environment variable for Flask (not strictly needed, but nice)
ENV FLASK_ENV=production

# 9. Start the app with gunicorn
#    - "app:app" means `app.py` file, `app` Flask instance
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
