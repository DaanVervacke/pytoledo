# pyToledo
![GitHub release (latest by date)](https://img.shields.io/github/v/release/DaanVervacke/pyToledo)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/DaanVervacke/pyToledo)
![GitHub Repo stars](https://img.shields.io/github/stars/DaanVervacke/pyToledo)


pyToledo is a Python library to interact with the common virtual learning environment for the Association KU Leuven a.k.a Toledo.

## Motivation
My goal was to provide an easy way to interact with the various KU Leuven API endpoints.

This library reproduces the Toledo portal login flow and returns a requests Session object that keeps track of your cookies and headers.

With this basic session object you can query these endpoints:
  - Enrollments
  - Upcoming courses
  - Events (messages and updates)

Optionally:
1. Extend this basic session with kuloket cookies. This allows you to query the following endpoints:
    - Schedule
2. Extend this basic session with toledo dashboard cookies. This allows you to query the following endpoints:
    - Todo (tasks and tests)


Good to know:

- Data will always be returned as JSON via stdout. You can redirect the output to any file using '>'.

- Tested on Windows 11 & Ubuntu 20.04
- Teacher accounts (u) are not supported!
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyToledo.

```bash
pip install pytoledo
```

## Usage
### As a package

```python
from toledo import portal
from toledo import kuloket
from toledo import dashboard
from toledo import api

# Create a portal session object 
portal_session = portal.create_session_object(
    user='',
    password=''
)

# Optionally extend the portal session with kuloket cookies
extendend_session = kuloket.extend_session(
    portal_session=portal_session
)
# and/or dashboard cookies
extendend_session = dashboard.extend_session(
    portal_session=portal_session
)

# Create an api object
toledo = api.create_api_object(
    session=extended_session
)
```
#### Examples
##### Enrollments/courses
```python
# returns all your courses in JSON
toledo.get_enrollments()
```
##### Upcoming courses
```python
# returns your upcoming courses (for today) in JSON
toledo.get_upcoming()
```
##### Events (messages & updates)
```python
# returns your messages in JSON
toledo.get_events(type='message')

# returns your updates in JSON
toledo.get_events(type='update')
```
##### Todo (tasks & tests)
```python
# returns your tasks in JSON
toledo.get_to_do(type='task')

# returns your tests in JSON
toledo.get_to_do(type='test')
```
##### Schedule
```python
# returns your schedule in JSON
toledo.get_schedule()
```
### As a script
```bash
optional arguments:
  -h, --help            show this help message and exit

  --enrollments, -en    retrieve all your enrollments

  --todo {task,test}, -td {task,test}
                        retrieve your to-do list (tasks or tests)

  --upcoming, -up       retrieve your upcoming courses

  --events {message,update}, -ev {message,update}
                        retrieve your recent events (messages or updates)

  --schedule, -sc       retrieve your schedule

  --rnumber RNUMBER, -rn RNUMBER
                        your personal rnumber

  --password PASSWORD, -pw PASSWORD
                        your password

  --silent, -s          surpress output
```
#### Examples
##### Enrollments/courses
```bash
python -m toledo --enrollments --rnumber yourrrnumber --password yourpassword
```
##### Upcoming courses
```bash
python -m toledo --upcoming --rnumber yourrrnumber --password yourpassword
```
##### Events (messages & updates)
```bash
# Messages
python -m toledo --events message --rnumber yourrrnumber --password yourpassword
# Updates
python -m toledo --events update --rnumber yourrrnumber --password yourpassword
```
##### Todo (tasks & tests)
```bash
# Tasks
python -m toledo --todo task --rnumber yourrrnumber --password yourpassword
# Tests
python -m toledo --todo test --rnumber yourrrnumber --password yourpassword
```
##### Schedule
```bash
python -m toledo --schedule --rnumber yourrrnumber --password yourpassword
```
## TODO
- Documentation
- Tests

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)