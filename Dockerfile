FROM python:3.8

EXPOSE 8080

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app

# Switching to a non-root user
RUN useradd appuser && chown -R appuser: /app
USER appuser

COPY --chown=appuser manage.py /app/.
COPY --chown=appuser jogging_tracker /app/jogging_tracker
COPY --chown=appuser api /app/api

# During debugging, this entry point will be overridden.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "jogging_tracker.wsgi"]
