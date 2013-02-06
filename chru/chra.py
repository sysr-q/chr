# -*- coding: utf-8 -*-

"""
    chra is the default entry-point for chr.
    Specifically, chru.chra:main is the entry point we use.
"""

from version import __version__, __supported__

import argparse
import os
import sys

import mattdaemon

class daemon(mattdaemon.daemon):
    def run(self, *args, **kwargs):
        """ This method will simply import the web control,
            set up the Flask app, and then run the app.
        """
        import web
        import web.routes
        setup = web.routes.set_app(
            debug=kwargs.get("debug"),
            settings_file=kwargs.get("settings")[0],
            log_file=kwargs.get("log"),
            __supported__=__supported__,
            update_schema=kwargs.get("update_schema")
        )
        if setup:
            web.routes.app.run(host=web.s.flask_host, port=web.s.flask_port)

def main():
    """ This method is in charge of everything

        It uses argparse to control the lovely arguments it handles,
        and sets up -- and controls -- the chr daemon.
    """
    if "--make-config" in sys.argv:
        import json
        import web
        print json.dumps(web.skeleton, indent=4)
        return

    parser = argparse.ArgumentParser(description="Take control of the chr url shortener.")
    parser.add_argument("action",
                        help="Action to take on the server",
                        choices=["start", "stop", "restart", "status", "-"],
                        metavar="action")

    parser.add_argument("-v", "--version",
                        help="Print the chr version and exit",
                        action="version",
                        version=__version__)

    parser.add_argument("-n", "--no-daemon",
                        help=argparse.SUPPRESS,
                        action="store_true")

    parser.add_argument("-l", "--log",
                        help="Set the file that output is logged to (default: %(default)s)",
                        type=str,
                        nargs=1,
                        metavar="file",
                        default="/tmp/chr-daemon.log")

    parser.add_argument("-p", "--pid",
                        help="Set the file the PID is saved to (default: %(default)s)",
                        type=str,
                        nargs=1,
                        metavar="file",
                        default="/tmp/chr-daemon.pid")

    parser.add_argument("-s", "--settings",
                        help="Set the location of the settings.json file",
                        type=file,
                        nargs=1,
                        metavar="file")

    # Not actually used via argparse.
    parser.add_argument("--make-config",
                        help="Print the settings.json file skeleton to stdout",
                        action="store_true")

    parser.add_argument("--update-schema",
                        help="Forcefully update the database schema, creating missing tables",
                        action="store_true")

    parser.add_argument("--api-manage",
                        help="Jump into the CLI API key manager",
                        action="store_true")

    parser.add_argument("--api-dump",
                        help="Dump the API keys as a JSON dict to stdout",
                        action="store_true")

    args = parser.parse_args()

    if args.api_manage:
        if not args.settings:
            print "You must pass in the settings.json file location (see --help for info)"
            return
        import api.manager
        cli = api.manager.cli(args.settings[0])
        cli.main()
        return

    if args.api_dump:
        if not args.settings:
            print "You must pass in the settings.json file location (see --help for info)"
            return
        import api.manager
        dump = api.manager.dump(args.settings[0])
        dump.dump()
        return

    daem_args = {
        "stdin": "/dev/null",
        "stdout": args.log,
        "stderr": args.log
    }
    if args.no_daemon:
        daem_args = {
            "stdin": "/dev/stdin",
            "stdout": "/dev/stdout",
            "stderr": "/dev/stderr"
        }
    daem = daemon(args.pid, daemonize=not args.no_daemon, **daem_args)

    if args.action == "start":
        if not args.settings:
            print "You must pass in the settings.json file location (see --help for info)"
            return

        # -n flag given? -- enable debugging
        debug = args.no_daemon
        daem.start(debug=debug, log=args.log, settings=args.settings, update_schema=args.update_schema)
    elif args.action == "stop":
        daem.stop()
    elif args.action == "restart":
        daem.restart()
    elif args.action == "status":
        if daem.status():
            print "chr currently running! :D"
        else:
            print "chr not running! D:"
        return
    elif args.action == "-":
        pass


if __name__ == "__main__":
    main()