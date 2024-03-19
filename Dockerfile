FROM python:3.12
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry install --no-dev
COPY . /app
CMD ["entrypoint.sh"]
