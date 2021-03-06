# Jogging Tracker REST API

QA Server:

https://jogging-tracker-api.herokuapp.com/api/v1

Download API schema: https://jogging-tracker-api.herokuapp.com/api/v1/schema.json (then you can import it to Postman)


# Task

Write a REST API that tracks jogging times of users

- API Users must be able to create an account and log in.
- All API calls must be authenticated.
- Implement at least three roles with different permission levels: a regular user would only be able to CRUD on their owned records, a user manager would be able to CRUD only users, and an admin would be able to CRUD all records and users.
- Each time entry when entered has a date, distance, time, and location.
- Based on the provided date and location, API should connect to a weather API provider and get the weather conditions for the run, and store that with each run. **see dev notes**
- The API must create a report on average speed & distance per week.
- The API must be able to return data in the JSON format.
- The API should provide filter capabilities for all endpoints that return a list of elements, as well should be able to support pagination.
- The API filtering should allow using parenthesis for defining operations precedence and use any combination of the available fields. The supported operations should at least include or, and, eq (equals), ne (not equals), gt (greater than), lt (lower than).
- Example -> (date eq '2016-05-01') AND ((distance gt 20) OR (distance lt 10)).
- Write unit and e2e tests.

# Running

with docker:
``` 
docker-compose up -d --build
```
## Login/Logout

```
# Login
$ curl "http://localhost:8080/api/v1/auth/login" -H 'Content-Type: application/json' -d '{"username":"myuser","password":"secretpass"}'
{"token":"4a1942e8a9886b1d83b5315113186abceed7ee2b"}

# Logout
$ curl "http://localhost:8080/api/v1/auth/logout" -H 'Authorization: token 4a1942e8a9886b1d83b5315113186abceed7ee2b'

```


# Testing

Unit testing: `pytest tests`

Integration tests: `pytest tests_integration`


# TODO List

- [x] Create Django project
- [x] Docker
- [x] Create Models
  - [x] User (django)
  - [x] Activity
  - [x] Weather
  - [x] Role (regular, manager, admin)
  - [x] Permissions
    - [x] Activities
    - [x] Users
- [x] CRUD 
  - [x] Activities
  - [x] Weather
  - [x] Users
- [x] Unit testing (never ending task...)
- [x] REST API
  - [x] CRUD User
  - [x] CRUD Activity (simple version)
- [x] Integration testing (never ending task...)
- [x] Authentication & Authorization
  - [x] Authentication
  - [x] Authorization
  - [x] Roles & Permissions
- [x] Weather API connector
- [x] Filtering
  - [x] Simple filtering
  - [x] Pagination
  - [x] Advanced filtering
- [x] Reports
  - [x] Average speed + Total distance / week
- [x] Revisions and manual tests
  - [x] fix need for user on create activity
  - [x] fix date / hour fields
  - [x] fix previlege escalation
- [x] Get it Production ready
- [x] Deploy



## Dev notes

1. The Weather provider needs a PRO account in order to provide historical data. Currently, this code is harcoded to request current weather only.
2. Could be using GIS on Spacial context (Activity coordinates), but there is just too much complexity for this exercise.
   1. must use geo-django
   2. postgresql must support postgis
   3. tests must start using SpaciaLite (dev system dependency outside python env)
   4. must install extra packages on Docker container
   5. more complexity
3. Requests to external API should be handled assyncronously when possible.
   1. An external request is slow
   2. an external API service may be temporarily down, have performance issues, change the API
   3. for non-critical data (such as the weather), it could be async-fetched 
   4. I will NOT implement it in this project because it's out of the scope, but I would go for something like this:
      1. Install celery for handling async tasks:
         1. add software dependencies
         2. add queueing service (redis/rabbitmq/...)
         3. add celery beat service
         4. add celery worker
      2. when creating a new activity, create a new task for consuming the external API for getting the weather. 
      3. task would fetch data and update activity with it
