# pyToledo
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/DaanVervacke/pyToledo)
![GitHub Repo stars](https://img.shields.io/github/stars/DaanVervacke/pyToledo)


pyToledo is a Python library to interact with the common virtual learning environment for the Association KU Leuven a.k.a Toledo.

## Motivation
My goal was to provide an easy way to interact with the various KU Leuven API endpoints.

This library reproduces the Toledo login flow and returns a requests Session object that keeps track of your cookies and headers.

The Session object allows you to query the various endpoints.

Good to know:

- Data will always be returned as JSON via stdout. You can redirect the output to any file using '>'.

- Tested on Windows 11 & Ubuntu 20.04
- Teacher accounts (u) are not supported!
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyToledo.

```bash
pip install toledo
```

## Usage
### As a package

```python
from toledo import login
from toledo import api

# Create a session object | returns a requests Session object with the necessary cookies and headers
session = login.create_session_object(
    user='',
    password=''
)

# Create an api object with your session
toledo = api.create_api_object(
    session=session
)
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

  --rnumber RNUMBER, -rn RNUMBER
                        your personal rnumber

  --password PASSWORD, -pw PASSWORD
                        your password

  --silent, -s          surpress output

```

## Examples
### Enrollments/courses
```python
# returns all your courses in JSON
toledo.get_enrollments()
or
python -m toledo -en
```
### Todo (tasks & tests)
```python
# returns open tasks in JSON
toledo.get_to_do(type='task')
or
python -m toledo -td task

# returns open tests in JSON
toledo.get_to_do(type='test')
or
python -m toledo -td test
```
### Upcoming courses
```python
# returns your upcoming courses (for a certain day) in JSON
toledo.get_upcoming()
or
python -m toledo -up
```
### Events (messages & updates)
```python
# returns your messages in JSON
toledo.get_events(type='message')
or
python -m toledo -ev message

# returns your updates in JSON
toledo.get_events(type='update')
or
python -m toledo -ev update
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)