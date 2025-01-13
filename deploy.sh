#!/bin/bash
cd /sources/django-bitza
git pull origin main
docker compose down
docker compose up -d --build