FROM python:3.12.3-slim

# install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# install poetry
RUN pip install poetry

# create working directories
WORKDIR /app

# copy poetry files
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-root --no-interaction --no-ansi

# copy the rest of the code
COPY . /app

# default command
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
