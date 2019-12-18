#!/usr/bin/python3
""" Command line utility that backs-up MySQL DB, additionally copies files if start of
month.
"""
import os
import json
import subprocess as subp
import shutil as sh
import argparse

# import datetime as dt
# import tarfile
import debug_control as dbc
import backup_utility as bu


def mysql_backup_call(command_list, dest, dbg=False):
    """ Key function that calls mysqldump to (or user specified) function to backup database"""

    file_ptr = open(dest, "a")

    call_rslt = subp.run(
        command_list, stdout=file_ptr, stderr=subp.PIPE, stdin=subp.PIPE
    )
    if call_rslt.returncode != 0:
        dbc.error_helper("MySQL Backup Error:", call_rslt.stderr, post=None, dbg=dbg)

    else:
        if call_rslt.stdout is not None:
            dbc.print_helper(("Successful MySQL  Backup" + call_rslt.stdout), dbg)
        else:
            out_str = "--".join(["Successful MySQL Backup", " ".join(command_list)])
            dbc.print_helper(out_str, dbg)
    file_ptr.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initial MySQL Schema Backup tool"
    )

    parser.add_argument(
        "-b", "--backup_dir", default="/mnt/droboP/backups/MySQL", type=str
    )
    parser.add_argument("-f", "--debug_file", type=str)
    parser.add_argument("-i", "--db_host_ip", default="127.0.0.1", type=str,
                        help="IP address of server where MySQL DB operates -- def: 127.0.0.1")

    parser.add_argument(
        "-l", "--items", default="example,introSQL,intermedSQL,Investing,jobsearch", type=str,
        help="Schema on the DB to backup"
    )
    parser.add_argument("-n", "--tool", default="/usr/bin/mysqldump", type=str)
    parser.add_argument("-o", "--options", default=None, type=str)
    parser.add_argument("-p", "--password", type=str)

    parser.add_argument("-u", "--user", default="spennington", type=str)
    parser.add_argument("-v", "--verbose", default=0, type=int)
    parser.add_argument("-w", "--temp_dir", default="/home/spennington/workspace", type=str,
                        help="Working directory where files are backed-up")

    args = parser.parse_args()
    args_dict = vars(args)

    if "password" in args_dict.keys() and args_dict["password"] is not None:
        # key variables must exist: args_dict (temp_dir], tables & base
        tables = args.items.replace(" ", "")
        tables = tables.split(",")
        base = [args.tool, "-h", args.db_host_ip, "-u", args.user, "-p"]
    elif "options" in args_dict.keys() and args_dict['options'] is not None and\
            isinstance(args_dict["options"], str) and len(args_dict["options"]) > 0:
        with open(args_dict['options']) as fp:
            args_dict = json.load(fp)

        if args.verbose > 0:
            args_dict["verbose"] = args.verbose
        else:
            if "verbose" not in args_dict.keys() and "debug_file" not in args_dict.keys():
                args_dict["verbose"] = 0

        if "items" in args_dict.keys() and isinstance(args_dict["items"], list):
            tables = args_dict["items"]
        else:
            raise ValueError("Application requires set of DB Schema to backup")

        tool = "/usr/bin/mysqldump"
        if "tool" in args_dict.keys():
            tool = args_dict["tool"]

        if "auth" in  args_dict.keys():
            base = [tool, "=".join(["--login-path", args_dict["auth"]])]
        else:
            raise ValueError("Auth Required")

    else:
        # dbc.print_helper("Password must be included", dbg=dbg)
        raise ValueError("Incomplete Specification")

    dbg, print_dbg = bu.calc_debug_levels(args_dict)

    dest, dt_str = bu.calc_directory(args_dict["temp_dir"], dbg=dbg)
    if os.path.exists(dest):
        dbc.print_helper(("Directory Exists: " + dest + os.linesep), dbg=dbg)
    else:
        os.mkdir(dest)

    os.chdir(dest)
    for tbl in tables:
        tbl_dest = "".join([os.sep.join([dest, tbl]), ".sql"])
        backup_list = base.copy()
        backup_list.append(tbl)
        mysql_backup_call(backup_list, tbl_dest, dbg=dbg)

    os.chdir("../")
    tarfilename, _ = bu.construct_gzip(args_dict["temp_dir"], dt_str, dbg=dbg)
    if tarfilename is not None:
        base_str = "Moving " + tarfilename + " to " + args_dict["backup_dir"]
        dbc.print_helper(base_str, dbg=dbg)
        sh.move(tarfilename, args_dict["backup_dir"])
        sh.rmtree(dt_str)

    else:
        dbc.print_helper("tarfilename is None -- review tar process", dbg=dbg)
    # bu.apply_rsync(args.temp_dir, dest, "Back-up", dbg=dbg)
