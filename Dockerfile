FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pip and poetry
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir poetry==2.1.1

# Set up working directory
WORKDIR /app

# Copy only poetry related files first (for better caching)
COPY poetry.lock pyproject.toml ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (Poetry 2.1.1 syntax)
RUN poetry install --no-root --no-interaction

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
