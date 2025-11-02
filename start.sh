#!/bin/bash
exec gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app.main:app
