# Task

Write a REST API that tracks jogging times of users

- API Users must be able to create an account and log in.
- All API calls must be authenticated.
- Implement at least three roles with different permission levels: a regular user would only be able to CRUD on their owned records, a user manager would be able to CRUD only users, and an admin would be able to CRUD all records and users.
- Each time entry when entered has a date, distance, time, and location.
- Based on the provided date and location, API should connect to a weather API provider and get the weather conditions for the run, and store that with each run.
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

# TODO List

- [x] Create Django project
- [x] Docker
- [ ] Create Models
  - [x] User (django)
  - [x] Activity
  - [x] Weather
  - [ ] Role (regular, manager, admin)
  - [ ] Permissions
    - [ ] Activities
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
- [ ] Weather API connector
- [ ] Filtering
  - [x] Simple filtering
  - [ ] Pagination
  - [ ] Advanced filtering
- [ ] Reports
  - [ ] Average speed + Total distance / week
