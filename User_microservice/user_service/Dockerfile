FROM python:3.12

LABEL maintainer="Syed Hamad Ali"
# Set the working directory in the container
WORKDIR /code
# Install system dependencies required for potential Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    protobuf-compiler \ 
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY . /code/
RUN poetry config virtualenvs.create false

RUN poetry install

EXPOSE 8001
CMD ["poetry", "run", "uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--reload", "--log-level", "debug"]



