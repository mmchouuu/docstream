FROM python:3.8-slim

# Set working directory in container
WORKDIR /app

# Install basic build tools and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code files
COPY src/ ./src/

# Create runtime directories
RUN mkdir -p data/raw data/markdown data/state logs

# Configure PYTHONPATH so python can locate the src module
ENV PYTHONPATH=/app

# Set default environment variables
ENV HELP_CENTER_API_URL="https://support.optisigns.com/api/v2/help_center"
ENV HELP_CENTER_PAGE_URL="https://support.optisigns.com"

# Set script execution entry point
CMD ["python", "-m", "src.main"]
