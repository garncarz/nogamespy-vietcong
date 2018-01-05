#!/usr/bin/env python3

import argparse
import logging

from nogamespy import tasks


arg_parser = argparse.ArgumentParser('Vietcong 1 master server crawler/replicator')
arg_parser.add_argument('--new', nargs='?', metavar='IP', const='Qtracker', default=False,
                        help='Pull new servers from Qtracker / IP of another master server.')
arg_parser.add_argument('--refresh', action='store_true', help='Refresh all saved servers.')
arg_parser.add_argument('--register', metavar=('IP', 'PORT'), nargs=2, help='Register new game server.')
arg_parser.add_argument('--master', action='store_true', help='Run master server.')
arg_parser.add_argument('--heartbeat', action='store_true', help='Run heartbeat server.')


def main():
    logging.basicConfig(
        level=logging.DEBUG,
    )

    args = arg_parser.parse_args()

    if args.new:
        tasks.pull_master(args.new if args.new.lower() != 'qtracker' else None)
    if args.refresh:
        tasks.refresh_all_servers()
    if args.register:
        tasks.register(*args.register, print_it=True)
    if args.master:
        tasks.run_master_server()
    if args.heartbeat:
        tasks.run_heartbeat_server()


if __name__ == '__main__':
    main()
