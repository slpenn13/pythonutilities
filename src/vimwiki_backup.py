#!/usr/bin/python3
""" Command line utility that backs-up vimwiki directory, additionally copies files if start of
month.
"""
import os
import json
# import shutil as sh
import argparse
import shutil as sh
import debug_control as dbc

# import mysql_backup as mbu
import backup_utility as bu


def update_file(src, file_filter, day=1, split='.', dbg=False):
    """ takes source directory (src) and initial filename and based on split constructs new file """

    filename = file_filter + ".wiki"
    proposed_file = bu.calc_filename(filename, split=split, include_time=False,
                                     dbg=dbg)

    loc = proposed_file.find(split)
    if loc > -1:
        day = str(day) if day > 9 else ("0" + str(day))
        prop_file = list(proposed_file)
        prop_file[loc-2] = day[0]
        prop_file[loc-1] = day[1]
        proposed_file = "".join(prop_file)

    base = "_".join([file_filter, "0000"])
    init_base = "_".join([file_filter, "0000"])

    for itm in os.listdir(src):
        if itm.startswith(file_filter):
            if base < itm:
                base = itm
    if base != proposed_file and proposed_file not in set(os.listdir(src)) and\
            base != init_base:
        sh.copy((src + os.sep + base), (src + os.sep + proposed_file))
        dbc.print_helper(("update_file Creating New File: " + proposed_file), dbg=dbg)
    elif base == init_base:
        dbc.print_helper("update_file created NO file (no item found)", dbg=dbg)
    else:
        dbc.print_helper("update_file created NO file", dbg=dbg)

def update_files(src, dest, temp, excluded_ending=None, dbg=False):
    """ walks directory structure in src, and compares to dest files
    excluded_ending is None removes items [".swo", ".swp", ".pyc", ".o", ".gz"], for all pass in []
    """
    init_index = -1
    init_len = len(str(src).split(os.sep))
    excluded_final = None

    if excluded_ending is None:
        excluded_final = set([".swo", ".swp", ".pyc", ".o", ".gz"])
    else:
        excluded_final = set(excluded_ending)

    for dirpath, _, filenames in os.walk(src):
        dir_split = str(dirpath).split(os.sep)
        cur_len = len(str(dirpath).split(os.sep))
        cur_index = init_index + (init_len - cur_len)
        cur_append = os.sep.join(dir_split[cur_index:])
        cur_dir = os.sep.join([dest, cur_append])
        dbc.print_helper(
            " ".join([str(cur_len), str(cur_index), cur_append, cur_dir]), dbg=dbg
        )

        not_empty = True
        if os.path.exists(cur_dir):
            base_dest_set = set(os.listdir(cur_dir))
        else:
            not_empty = False
            os.mkdir(cur_dir)

        for filename in filenames:
            _, init_splt = os.path.splitext(filename)

            # print(filename + " " + str(init_splt) + " " + str(not_empty) + " " + cur_dir)
            if init_splt != '' and init_splt in excluded_final:
                dbc.print_helper(("Excluding " + filename), dbg=dbg)
            else:
                temp_dir = os.sep.join([temp, cur_append])
                if not os.path.exists(temp_dir):
                    os.mkdir(temp_dir)

                if not_empty and filename in base_dest_set:
                    bu.calc_diff(dirpath, cur_dir, temp_dir, filename, inc_backup=["index.wiki"],
                                 dbg=dbg)
                else:
                    dbc.print_helper(("Adding " + filename), dbg=dbg)
                    sh.copy(os.sep.join([dirpath, filename]), temp_dir)
                    sh.copy(os.sep.join([dirpath, filename]), cur_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initial Vimwiki backup tool and updater"
    )

    parser.add_argument("-b", "--backup_dir", default="/mnt/droboP/backups", type=str,
                        help="Directory where wikis will be backed to")
    parser.add_argument("-f", "--debug_file", type=str)

    parser.add_argument("-n", "--new", type=str, help="Construct new files")
    parser.add_argument("-o", "--options", default=None, type=str)
    parser.add_argument("-s", "--src", default="/home/spennington/vimwiki", type=str,
                        help="Directory containing wikis to backup")
    parser.add_argument("-u", "--update", default=0, type=int)
    parser.add_argument("-v", "--verbose", default=0, type=int)
    parser.add_argument(
        "-w", "--temp_dir", default="/home/spennington/workspace", type=str
    )

    args = parser.parse_args()
    args_dict = vars(args)
    if "options" in args_dict.keys() and args_dict["options"] is not None:
        with open(args_dict["options"], "r") as fp:
            args_dict = json.load(fp)

        if "temp_dir" not in args_dict.keys():
            raise ValueError("JSON must include temp_dir")

        if "src" not in args_dict.keys():
            raise ValueError("JSON must include src (source directory)")

        if "backup_dir" not in args_dict.keys():
            raise ValueError("JSON must include backup_dir")

        hostname = None
        if "hostname" in args_dict.keys():
            hostname = args_dict["hostname"]

        if args.verbose > 0:
            args_dict["verbose"] = args.verbose
        else:
            if "verbose" not in args_dict.keys() and "debug_file" not in args_dict.keys():
                args_dict["verbose"] = 0
            elif "debug_file" in args_dict.keys():
                args_dict["debug_file"] = bu.append_date_file(args_dict["debug_file"])
    else:
        if "backup_dir" not in args_dict.keys() or "src" not in args_dict.keys():
            raise ValueError("Dictionary Combination")

    dbg, print_dbg = bu.calc_debug_levels(args_dict)
    if "debug_file" in args_dict.keys():
        dbc.print_helper(("Using debug file " + args_dict["debug_file"]), dbg=dbg)

    if hostname is None:
        hostname = bu.calc_hostname(dbg=dbg)

    if hostname is not None:
        dest = os.sep.join([args_dict["backup_dir"], hostname])
    else:
        dest = args_dict["backup_dir"]

    temp, dt_str = bu.calc_directory(args_dict["temp_dir"], dbg=dbg)
    if not os.path.exists(temp):
        os.mkdir(temp)

    update_files(args_dict["src"], dest, temp, dbg=dbg)

    # zipfile construction
    os.chdir(args_dict["temp_dir"])
    dbc.print_helper(("Temp "  + args_dict["temp_dir"]), dbg=dbg)
    dbc.print_helper(("Dest: " + dest), dbg=dbg)

    zipname = bu.construct_zip(args_dict["temp_dir"], dt_str, dbg=dbg)
    # CLEANING UP
    if zipname is not None and os.path.exists(zipname):
        sh.move(zipname, dest)
    else:
        zipname = "EMPTY" if zipname is None else zipname
        dbc.print_helper(("Missing zip" + zipname), dbg=dbg)
    sh.rmtree(dt_str)
    # RSYNC
    if args_dict["update"] > 0:
        dest = dest + os.sep + "vimwiki"
        bu.apply_rsync(args_dict["src"], dest, "Back-up", dbg=dbg)
        if isinstance(dbg, dbc.debug_control):
            dbg.close()

    if args_dict["new"]:
        update_file(args_dict["src"], hostname, dbg=dbg)
