# Campaign Autopilot — Docker Image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir streamlit

# Create state directories
RUN mkdir -p .state output/content reports

# Expose port for Hugging Face Spaces
EXPOSE 7860

# Run the Streamlit dashboard on port 7860
CMD ["streamlit", "run", "dashboard/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
