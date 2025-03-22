# python image
FROM python:3.12

# working directory
WORKDIR /app

# copy project files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire FastAPI app
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]