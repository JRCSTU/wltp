#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

'''The command-line entry-point for using all functionality of WLTC tool.
'''
def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (__version__, program_build_date)
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2014 ankostis (manky.io)                                            \
                Licensed under the AGPLv3\nhttp://www.gnu.org/licenses/agpl.html"

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = argparse.ArgumentParser(epilog=program_longdesc, description=program_license)
        parser.add_argument("--url", help="set twisterd's listening url [default: %(default)s]", metavar="URL")
        parser.add_argument("--debug", action="store_true", help="set debug level [default: %(default)s]")
        parser.add_argument("--verbose", action="count", default=0, help="set verbosity level [default: %(default)s]")
        parser.add_argument("--version", action="version", version=program_version_string, help="prints version identifier of the program")

        # set defaults
        parser.set_defaults(url="http://user:pwd@127.0.0.1:28332")

        # process options
        opts = parser.parse_args(argv)

        if opts.debug:
            DEBUG = opts.debug
            print("debug = %d" % DEBUG)
        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)
        if opts.url:
            print("url = %s" % opts.url)

        # MAIN BODY #
        collect_users(opts.url)

    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'twanky_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
