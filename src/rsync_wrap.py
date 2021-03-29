#!/usr/bin/python3
""" Rsync wrapper intended to sync drives.
"""
import subprocess as subp
import os
# import sys
# import shutil as sh
import datetime as dt
# import tarfile
# import zipfile as zp
# import debug_control as dbc
# import json
import argparse
# import datetime as dt
# import tarfile
import debug_control as dbc
import backup_utility as bu


def exec_rsync(opt, dbg=False, print_dbg=False):
    ''' executes calls to rsync '''
    if 'dest' not in opt.keys() or 'source' not in opt.keys():
        raise ValueError("Destination and Source must exist in the options file")

    if opt['reverse']:
        dest = opt['source']
        source = opt['dest']
    else:
        dest = opt['dest']
        source = opt['source']


    if os.path.exists(dest):
        dbc.print_helper(("Directory Exists: " + dest + os.linesep), dbg=dbg)
    else:
        os.mkdir(dest)

    """ copies files from src (init_base_dir) to dest (init_rslt_dir)
    """
    print_dbg = dbc.test_dbg(dbg)

    rsync_list = [
        "rsync",
        opt['base'],
        opt['delete'],
        "--info=SKIP,STATS",
        opt["exclusion"],
        (source + os.sep),
        dest
    ]

    split = source.split(os.sep)
    itm = split[len(split)-1]

    base_str = "".join(["RSYNC: --", " ".join(rsync_list), os.linesep])
    dbc.print_helper(base_str, dbg)

    call_rslt = subp.run(rsync_list, stdout=subp.PIPE, stderr=subp.PIPE)
    if call_rslt.returncode != 0:
        dbc.error_helper("RSYNC Error:", call_rslt.stderr, post=itm, dbg=dbg)
    else:
        if print_dbg:
            if isinstance(dbg, bool):
                base_time_str = dt.datetime.now()
                print(
                    "".join(
                        [
                            call_rslt.stdout.decode("UTF-8"),
                            os.linesep,
                            base_time_str.strftime("%Y/%m/%d %H:%M:%S"),
                        ]
                    )
                )

            else:
                dbg.write_stdout(itm, call_rslt.stdout)
# bu.apply_rsync(args.temp_dir, dest, "Back-up", dbg=dbg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="rsync wrapper tool"
    )

    parser.add_argument("-b", "--backup_dir", default="projects", type=str,
                        help="base directory to backup")
    parser.add_argument("-d", "--delete", default=0, type=int,
                        help="delete indicator > 1 => --delete")
    parser.add_argument("-f", "--exclude_file", default="", type=str,
                        help="exclude file ... must follow rsync format")
    parser.add_argument("-n", "--dryrun", default=0, type=int,
                        help="dry-run indicator > 1")
    parser.add_argument("-r", "--reverse", default=0, type=int,
                        help="reverse indicator > 1")

    parser.add_argument("-s", "--source", default="", type=str,
                        help="source directory")
    parser.add_argument("-t", "--destination", default="", type=str,
                        help="destination directory")

    parser.add_argument("-v", "--verbose", default=0, type=int)


    parser.add_argument(
        "-l", "--items", default="example,introSQL,intermedSQL,Investing,jobsearch", type=str,
        help="Schema on the DB to backup"
    )
    parser.add_argument("-o", "--options", default=None, type=str)

    parser.add_argument("-u", "--user", default="spennington", type=str)
    parser.add_argument("-w", "--temp_dir", default="/home/spennington/workspace", type=str,
                        help="Working directory where files are backed-up")

    args = parser.parse_args()
    args_dict = vars(args)

    opt = {}

    base = "-a" + ("v" if args.verbose > 0 else "")
    opt['base'] = base + ("d" if args.dryrun > 0 else "")
    opt['delete'] = ("--delete" if args.delete > 0 else "")
    opt['exclusion'] = (('--exclude-from=\"' + args.exclude_file +'\"') if args.exlude_file and\
                         isinstance(args.exclude_file, str) and\
                         os.path.exists(args.exclude_file) else "--exclude=*.sw[op]")

    opt['reverse'] = bool(args.reverse > 0)

    if args.source:
        opt['source'] = args.source
    else:
        raise ValueError("Source must be provided and non empty string")

    if args.destination:
        opt['dest'] = args.destination
    else:
        raise ValueError("Destination must be provided and non empty string")

    dbg, print_dbg = bu.calc_debug_levels(args_dict)

    exec_rsync(opt, dbg, print_dbg)
