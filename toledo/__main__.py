# __main__.py

import argparse
import configparser
import os

from login import create_session_object
from api import create_api_object
from out import ToledoOutput


def main(args):

    confparser = configparser.ConfigParser()
    confparser.read('config.txt')

    session = create_session_object(
        user=confparser.get('USER', 'RNumber'),
        password=confparser.get('USER', 'Password')
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        epilog='', usage=argparse.SUPPRESS)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--enrollments', '-en', help='retrieve all your enrollments', action='store_true')
    group.add_argument(
        '--todo', '-t', help='retrieve your to-do list (tasks, tests or all)', choices=['task', 'test'])
    group.add_argument(
        '--upcoming', '-u', help='retrieve your upcoming courses', action='store_true')
    group.add_argument(
        '--events', '-ev', help='retrieve your recent events (messages or updates)', choices=['message', 'update'])

    parser.add_argument(
        '--output', '-o', help='specify outputname (without extension!)', required=True, nargs=1)
    parser.parse_args()

    main(parser.parse_args())
