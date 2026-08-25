FROM python:3.11-slim-bookworm

# Install system dependencies for GDAL, postgis, and other geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    gdal-bin \
    libproj-dev \
    proj-bin \
    libgeos-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL compilation
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .

# Filter out GDAL from requirements.txt to install it matching the system libgdal version
RUN grep -v "gdal==" requirements.txt > reqs.txt && \
    pip install --no-cache-dir -r reqs.txt && \
    pip install --no-cache-dir gdal==$(gdal-config --version)

# Copy the rest of the application
COPY . .

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=300 -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
