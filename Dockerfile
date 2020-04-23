FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

RUN mkdir /code
WORKDIR /code

# poetry export -f requirements.txt -o requirements.txt
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY jogging_tracker /code/jogging_tracker
COPY manage.py /code/

# change this in production:
CMD python manage.py runserver 0:$PORT
