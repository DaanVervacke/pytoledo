# pytoledo

![GitHub release (latest by date)](https://img.shields.io/github/v/release/DaanVervacke/pyToledo)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/DaanVervacke/pyToledo)
![GitHub Repo stars](https://img.shields.io/github/stars/DaanVervacke/pyToledo)

pytoledo is a Python library to interact with the common virtual learning environment for the Association KU Leuven a.k.a Toledo.

**v3.0.0 adds support for KU Leuven Authenticator, which is now mandatory for all students**

**v3.1.0 adds the ability to query Vives Plus endpoints, please note that this might not work for Luca, Odisee, Thomas More and UCLL students!**

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
3. Create a Vives Plus session. This allows you to query the following endpoints:
    - Schedule (dynamic)
    - Student information
    - Notices
    - Dashboard

Good to know:

- Bypassing KU Leuven Authenticator prompts is possible by exporting and re-using your Vives Plus authorization token.
- Data will always be returned as JSON via stdout. You can redirect the output to any file using '>'.
- **Teacher accounts (u) are not supported!**

## Installation

### pip

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pytoledo.

```bash
pip install pytoledo --upgrade
```

## Usage

### As a package

##### Toledo

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
toledo_api = api.create_api_object(
    session=extended_session
)
```

##### Vives Plus

```python
from toledo import vivesplus
from toledo import api

# Create a Vives Plus session object from username & password
vivesplus_session = vivesplus.create_vivesplus_session_object(
    user='',
    password='',
)

# or from authorization token or file
vivesplus_session = vivesplus.create_vivesplus_session_object(
    authorization=''
)

# Create an api object
vivesplus_api = api.create_vivesplus_api_object(
    session=vivesplus_session
)
```

#### Examples

##### Toledo

###### Enrollments/courses

```python
# returns all your courses in JSON
toledo_api.get_enrollments()
```

###### Upcoming courses

```python
# returns your upcoming courses (for today) in JSON
toledo_api.get_upcoming()
```

###### Events (messages & updates)

```python
# returns your messages in JSON
toledo_api.get_events(type='message')

# returns your updates in JSON
toledo_api.get_events(type='update')
```

###### Todo (tasks & tests)

```python
# returns your tasks in JSON
toledo_api.get_to_do(type='task')

# returns your tests in JSON
toledo_api.get_to_do(type='test')
```

###### Schedule

```python
# returns your schedule in JSON
toledo_api.get_schedule()
```

##### Vives Plus

###### Export and re-use authorization token

```python
# login using username and password
vivesplus_session = vivesplus.create_vivesplus_session_object(
    user='',
    password='',
)
# Create an api object
vivesplus_api = api.create_vivesplus_api_object(
    session=vivesplus_session
)
# returns your authorization token in JSON
authorization = vivesplus_api.get_authorization_token()

# login using your authorization token
vivesplus_session = vivesplus.create_vivesplus_session_object(
    authorization=authorization['token']
)
```

###### Schedule

```python
# returns your schedule in JSON
vivesplus_api.get_schedule(
    start_date='2023-06-14',
    end_date='2023-06-22'
)
```

###### Student information

```python
# returns your student information in JSON
vivesplus_api.get_student_info()
```

###### Dashboard

```python
# returns your dashboard in JSON
vivesplus_api.get_dashboard()
```

###### Notices

```python
# returns your notices in JSON
vivesplus_api.get_notices()
```

### As a script

##### Toledo

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

##### Vives Plus

```bash
optional arguments:
  -h, --help            show this help message and exit

  --schedule, -sc       retrieve your schedule

  --student-info, -si   retrieve your student information

  --dashboard, -db      retrieve your dashboard

  --notices, -no        retrieve your notices

  --get-authorization-token, -gat 
                        retrieve your vives plus authorization token as a JSON file

  --set-authorization-token JSON TOKEN FILE, -sat JSON TOKEN FILE
                        set your vives plus authorization token by providing a JSON file

  --rnumber RNUMBER, -rn RNUMBER
                        your personal rnumber

  --password PASSWORD, -pw PASSWORD
                        your password

  --silent, -s          surpress output
```

#### Examples

##### Toledo

###### Enrollments/courses

```bash
python -m toledo toledo --enrollments --rnumber yourrrnumber --password yourpassword
```

###### Upcoming courses

```bash
python -m toledo toledo --upcoming --rnumber yourrrnumber --password yourpassword
```

###### Events (messages & updates)

```bash
# Messages
python -m toledo toledo --events message --rnumber yourrrnumber --password yourpassword
# Updates
python -m toledo toledo --events update --rnumber yourrrnumber --password yourpassword
```

###### Todo (tasks & tests)

```bash
# Tasks
python -m toledo toledo --todo task --rnumber yourrrnumber --password yourpassword
# Tests
python -m toledo toledo --todo test --rnumber yourrrnumber --password yourpassword
```

###### Schedule

```bash
python -m toledo toledo --schedule --rnumber yourrrnumber --password yourpassword
```

##### Vives Plus

###### Export and re-use authorization token

```bash
# Export
python -m toledo vivesplus --get-authorization-token --rnumber yourrrnumber --password yourpassword
# Re-use
python -m toledo vivesplus --set-authorization-token vivesplus_authorization_token_<yourrnumber>.json ... any other option
```

###### Schedule

```bash
python -m toledo vivesplus --set-authorization-token vivesplus_authorization_token_<yourrnumber>.json --schedule '2023-06-14' '2023-06-22'
```

###### Student information

```bash
python -m toledo vivesplus --set-authorization-token vivesplus_authorization_token_<yourrnumber>.json --student-info
```

###### Dashboard

```bash
python -m toledo vivesplus --set-authorization-token vivesplus_authorization_token_<yourrnumber>.json --dashboard
```

###### Notices

```bash
python -m toledo vivesplus --set-authorization-token vivesplus_authorization_token_<yourrnumber>.json --notices
```

## TODO

- Documentation
- Tests

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
