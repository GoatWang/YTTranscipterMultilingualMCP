FROM python:3.10-slim-buster

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY uv.lock ./ 

# Install dependencies using uv based on pyproject.toml
RUN /usr/local/bin/uv sync

COPY . .

CMD ["/usr/local/bin/python", "main.py"]