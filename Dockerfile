FROM python:3.12
WORKDIR /app
ENV PYTHONPATH=/app
COPY pyproject.toml poetry.lock /app/
COPY . /app
RUN pip install poetry && poetry config virtualenvs.create false && poetry install
CMD ["/app/entrypoint.sh"]
