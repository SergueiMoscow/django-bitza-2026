#!/bin/sh
poetry run gunicorn bitza.asgi:application -k uvicorn.workers.UvicornWorker
