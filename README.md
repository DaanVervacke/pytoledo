# pyToledo

pyToledo is a Python library to interact with the common virtual learning environment for the Association KU Leuven (Toledo).

## Motivation
My goal was to provide an easy way to interact with the various KU Leuven API endpoints.

This library reproduces the Toledo login flow and returns a requests Session object that keeps track of your cookies and headers.

The Session object allows you to query the various endpoints.

Data will always be returned in JSON.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pyToledo.

```bash
pip install toledo
```

## Usage

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

## Examples
### Enrollments/courses
```python
# returns all your courses in JSON
toledo.get_enrollments()
```
### Todo (tasks & tests)
```python
# returns open tasks in JSON
toledo.get_todo(type='task')

# returns open tests in JSON
toledo.get_todo(type='test')

# returns tasks, tests and various other stuff in JSON
toledo.get_todo(type='all')
```
### Upcoming courses
```python
# returns your upcoming courses (for a certain day) in JSON
toledo.get_upcoming()
```
### Events (messages & updates)
```python
# returns your messages in JSON
toledo.get_events(type='message')
# returns your updates in JSON
toledo.get_events(type='update')
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)