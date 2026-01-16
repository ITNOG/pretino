FROM python:3.13-slim

WORKDIR /app

COPY . .

# Install project dependencies using Poetry
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev 

# Expose the port your application listens on (adjust as needed)
EXPOSE 8000

# Set the entrypoint to run the application
ENTRYPOINT ["poetry", "run", "python", "-m", "pretino"]
