# __main__.py

import argparse
import sys
import json

from toledo.login import create_session_object
from toledo.api import create_api_object


def main(args):

    session = create_session_object(
        user=args.rnumber,
        password=args.password
    )

    api = create_api_object(
        session=session
    )

    if args.enrollments:

        output = api.get_enrollments()

    elif args.todo:

        output = api.get_to_do(
            type=args.todo
        )

    elif args.upcoming:

        output = api.get_upcoming()

    elif args.events:

        output = api.get_events(
            type=args.events
        )

    if not args.silent:

        json.dump(output, sys.stdout)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        epilog='', usage=argparse.SUPPRESS)

    optionsgroup = parser.add_mutually_exclusive_group(required=True)

    optionsgroup.add_argument(
        '--enrollments', '-en', help='retrieve all your enrollments', action='store_true')
    optionsgroup.add_argument(
        '--todo', '-td', help='retrieve your to-do list (tasks or tests)', choices=['task', 'test'])
    optionsgroup.add_argument(
        '--upcoming', '-up', help='retrieve your upcoming courses', action='store_true')
    optionsgroup.add_argument(
        '--events', '-ev', help='retrieve your recent events (messages or updates)', choices=['message', 'update'])

    parser.add_argument(
        '--rnumber', '-rn', help='your personal rnumber', nargs=1)
    parser.add_argument(
        '--password', '-pw', help='your password', nargs=1)

    parser.add_argument(
        '--silent', '-s', help='surpress output', action='store_true')
    parser.parse_args()

    main(parser.parse_args())
