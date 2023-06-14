# __main__.py

import argparse
import sys
import json

from toledo.portal import create_session_object
from toledo.dashboard import extend_session as dashboard_extend_session
from toledo.kuloket import extend_session as kuloket_extend_session
from toledo.vivesplus import create_vivesplus_session_object
from toledo.api import create_toledo_api_object
from toledo.api import create_vivesplus_api_object


def main(args):

    option = [ arg for arg, value in args.__dict__.items() if value and arg in ('enrollments', 'upcoming', 'events', 'schedule', 'todo', 'student_info', 'dashboard', 'notices', 'get_authorization_token', 'set_authorization_token')][0]

    if args.service == 'toledo':

        session = create_session_object(
            user=args.rnumber,
            password=args.password
            )

        if option in ('todo'):

            session = dashboard_extend_session(
            portal_session=session
            )
        
        elif option in ('schedule'):

            session = kuloket_extend_session(
            portal_session=session
            )

        toledo_api = create_toledo_api_object(
            session=session
        )

        match option:

            case 'enrollments':

                output = toledo_api.get_enrollments()
            
            case 'upcoming':

                output = toledo_api.get_upcoming()

            case 'events':

                output = toledo_api.get_events(
                    type=args.events
                )

            case 'schedule':

                output = toledo_api.get_schedule()
            
            case 'todo':

                output = toledo_api.get_to_do(
                type=args.todo
                )

    elif args.service == 'vivesplus':

        if None in (args.rnumber, args.password) and args.set_authorization_token is None:

            sys.exit('vivesplus: error: the following arguments are required: --rnumber/-rn, --password/-pw')

        authorization = args.set_authorization_token if args.set_authorization_token is not None else None

        session = create_vivesplus_session_object(
            user=args.rnumber,
            password=args.password,
            authorization=authorization
        )
        
        vivesplus_api = create_vivesplus_api_object(
            session=session
        )

        match option:

            case 'schedule':

                output = vivesplus_api.get_schedule(
                    start_date=args.schedule[0],
                    end_date=args.schedule[1]
                )

            case 'student_info':

                output = vivesplus_api.get_student_info()

            case 'dashboard':

                output = vivesplus_api.get_dashboard()

            case 'notices':

                output = vivesplus_api.get_notices()

            case 'get_authorization_token':

                output = vivesplus_api.get_authorization_token()  
    
    if not args.silent:

        if option != 'get_authorization_token':

            json.dump(output, sys.stdout)
        
        else:

            with open(f'vivesplus_authorization_token_{args.rnumber[0]}.json', 'w') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        epilog='', usage=argparse.SUPPRESS)
    
    subparsers = parser.add_subparsers(help='help for services', dest='service', required=True)

    toledo_parser = subparsers.add_parser('toledo', help='toledo help')

    toledo_parser.add_argument(
        '--rnumber', '-rn', help='your personal rnumber', nargs=1, required=True)
    toledo_parser.add_argument(
        '--password', '-pw', help='your password', nargs=1, required=True)

    vivesplus_parser = subparsers.add_parser('vivesplus', help='vivesplus help')

    toledo_optionsgroup = toledo_parser.add_mutually_exclusive_group(required=True)
    
    toledo_optionsgroup.add_argument(
        '--enrollments', '-en', help='retrieve all your enrollments', action='store_true')
    toledo_optionsgroup.add_argument(
        '--todo', '-td', help='retrieve your to-do list (tasks or tests)', choices=['task', 'test'])
    toledo_optionsgroup.add_argument(
        '--upcoming', '-up', help='retrieve your upcoming courses', action='store_true')
    toledo_optionsgroup.add_argument(
        '--events', '-ev', help='retrieve your recent events (messages or updates)', choices=['message', 'update'])
    toledo_optionsgroup.add_argument(
        '--schedule', '-sc', help='retrieve your schedule', action='store_true')
    
    vivesplus_optionsgroup = vivesplus_parser.add_mutually_exclusive_group(required=True)

    vivesplus_optionsgroup.add_argument(
        '--schedule', '-sc', nargs=2, metavar=('start_date', 'end_date'), help='retrieve your schedule')

    vivesplus_optionsgroup.add_argument(
        '--student-info', '-si', help='retrieve your student information', action='store_true')

    vivesplus_optionsgroup.add_argument(
        '--dashboard', '-db', help='retrieve your dashboard', action='store_true')
    
    vivesplus_optionsgroup.add_argument(
        '--notices', '-no', help='retrieve your notices', action='store_true')

    vivesplus_optionsgroup.add_argument(
        '--get-authorization-token', '-gat', help='retrieve your vives plus authorization token as a JSON file', action='store_true')

    vivesplus_parser.add_argument(
        '--set-authorization-token', '-sat', help='set your vives plus authorization token by providing a JSON file')

    vivesplus_parser.add_argument(
        '--rnumber', '-rn', help='your personal rnumber', nargs=1, required=False)
    vivesplus_parser.add_argument(
        '--password', '-pw', help='your password', nargs=1, required=False)


    toledo_parser.add_argument(
        '--silent', '-s', help='surpress output', action='store_true')
    
    vivesplus_parser.add_argument(
        '--silent', '-s', help='surpress output', action='store_true')
    
    main(parser.parse_args())
