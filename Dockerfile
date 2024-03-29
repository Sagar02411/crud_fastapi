# Set the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "application:app", "--host", "0.0.0.0", "--port", "8000"]