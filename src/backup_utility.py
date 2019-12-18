#!/usr/bin/python3
""" Python libray supporting backup utilities applied across newton & feynman"""
import subprocess as subp
import os
import sys
import shutil as sh
import datetime as dt
import tarfile
import zipfile as zp
import debug_control as dbc
import diskwalk_api as dwa


def calc_filename(name, split='.', include_time=False, dbg=False):
    """ inserts datetime information between first split and filename"""
    dt_str, time_str = calc_date_time()
    strt = str(name).split(split)
    res = ''

    if len(strt) == 1:
        res = strt[0]
    elif len(strt) > 1:
        append = split.join(strt[1:]) if len(strt) > 2 else strt[1]
        if include_time:
            res = "_".join([strt[0], dt_str, time_str])
        else:
            res = "_".join([strt[0], dt_str])
        res = res + split + append
    else:
        res = 'FAILED'

    dbc.print_helper(("calc_filename: " + res), dbg=dbg)

    return res

def calc_hostname(dbg=False):
    """" Calculates linux hostname"""
    rsync_list = ["cat", "/proc/sys/kernel/hostname"]
    hostname = None

    call_rslt = subp.run(rsync_list, stdout=subp.PIPE, stderr=subp.PIPE)
    if call_rslt.returncode != 0:
        dbc.error_helper("Hostname", call_rslt.stderr, post=None, dbg=dbg)
    else:
        hostname = call_rslt.stdout.decode("UTF-8").replace("\n", "")
        dbc.print_helper(("Hostname " + hostname), dbg=dbg)

    return hostname


def calc_diff(src, dest, temp, filename, inc_backup=None, dbg=False):
    """Calls UNIX diff function comparing files """
    src_str = os.sep.join([src, filename])
    dest_str = os.sep.join([dest, filename])
    if inc_backup is not None:
        inc_backup = set(inc_backup)

    val = str(filename).split(".")

    try:
        diff_str = "".join([temp, os.sep, val[0], ".diff"])
        diff_list = ["/usr/bin/diff", "-s", src_str, dest_str]

        call_rslt = subp.run(diff_list, stdout=subp.PIPE, stderr=subp.PIPE)
        init_rslt = call_rslt.stdout.decode("UTF-8")
        # print(str(call_rslt.returncode) + os.linesep + init_rslt)
        if call_rslt.returncode == 0 and init_rslt.endswith("identical" + os.linesep):
            base_str = "Excluding Identical File: " + filename
            dbc.print_helper(base_str, dbg=dbg)
        elif call_rslt.returncode == 1 and init_rslt is not None and\
                not init_rslt.endswith("identical" + os.linesep):
            file_ptr = open(diff_str, "w")
            file_ptr.write(init_rslt)
            file_ptr.close()

            if inc_backup is not None and filename in inc_backup:
                temp_filename = calc_filename(os.sep.join([temp, filename]), include_time=True,
                                              dbg=dbg)
                sh.copy(src_str, temp_filename)

            base_str = " ".join(["Diff", diff_str, "success"])
            dbc.print_helper(base_str, dbg=dbg)
        else:
            dbc.error_helper("Diff Error:", call_rslt.stderr, filename, dbg=dbg)
    except:
        dbc.error_helper("Diff Exception: ", stderr=None, post=filename, dbg=dbg)


def construct_gzip(src_dir, base_dir, base_name="MySQL_backup_",
                   excluded_ending=None, dbg=False):
    """ constructs tar.gz file based in src dir
    excluded_ending is None removes items [".swo", ".swp", ".pyc", ".o", ".gz"], for all pass in []
    """
    dt_str, time_str = calc_date_time()
    base_name = "_".join([base_name, dt_str, time_str])
    tarfilename = None
    excluded = []

    if excluded_ending is None:
        excluded_final = set([".swo", ".swp", ".pyc", ".o", ".gz"])
    else:
        excluded_final = set(excluded_ending)

    try:
        tarfilename = "".join([src_dir, os.sep, base_name, ".tar.gz"])
        with tarfile.open(tarfilename, "w:gz") as tar:
            dw = dwa.diskwalk(os.sep.join([src_dir, base_dir]))
            for itm in dw.enumeratePaths():
                _, init_splt = os.path.splitext(itm)

                # print(filename + " " + str(init_splt) + " " + str(not_empty) + " " + cur_dir)
                if init_splt != '' and init_splt in excluded_final:
                    base_str = ": ".join(["Excluding", itm])
                    dbc.print_helper(base_str, dbg=dbg)
                    excluded.append(itm)
                else:
                    itm_loc = str(itm).find(base_dir)
                    base_str = "--".join(["adding", itm[itm_loc:]])
                    tar.add(itm[itm_loc:])

            tar.close()
    except:
        tar.close()

    return tarfilename, excluded

def construct_zip(src_dir, base_dir, base_name="vimwiki_diff_backup", excluded_ending=None,
                  dbg=False):
    """ Construct zip file
    excluded_ending is None removes items line [".swo", ".swp", ".pyc", ".o", ".gz"],
        for all pass in []
    """
    dt_str, time_str = calc_date_time()
    base_name = "_".join([base_name, dt_str, time_str])
    zipname = None

    if excluded_ending is None:
        excluded_final = set([".swo", ".swp", ".pyc", ".o", ".gz"])
    else:
        excluded_final = set(excluded_ending)


    try:
        zipname = "".join([src_dir, os.sep, base_name, ".zip"])
        zip_count = 0
        with zp.ZipFile(zipname, mode='w') as zp_ptr:
            dw = dwa.diskwalk(os.sep.join([src_dir, base_dir]))
            for itm in dw.enumeratePaths():
                _, init_splt = os.path.splitext(itm)

                # print(filename + " " + str(init_splt) + " " + str(not_empty) + " " + cur_dir)
                if init_splt != '' and init_splt in excluded_final:
                    base_str = ": ".join(["Excluding", itm])
                    dbc.print_helper(base_str, dbg=dbg)
                else:
                    itm_loc = str(itm).find(base_dir)
                    base_str = "--".join(["adding", itm[itm_loc:]])
                    zp_ptr.write(itm[itm_loc:])
                    if not itm.endswith(base_dir):
                        zip_count = zip_count + 1

            zp_ptr.close()

            if zip_count < 2:
                dbc.print_helper("Warning construct_zip -- likely empty zip", dbg=dbg)
    except OSError as err:
        if zp_ptr is not None:
            zp_ptr.close()
        dbc.error_helper(("OSError: Zip" + err.strerror), stderr=None, post=zipname, dbg=dbg)
    except:
        if zp_ptr is not None:
            zp_ptr.close()
        dbc.error_helper(("Error: Zip"  + str(sys.exc_info()[0])), stderr=None, post=None, dbg=dbg)

    return zipname

def calc_date_time(join_char=""):
    """ Calculates Date & Time strings from datetime.now()"""
    dtn = dt.datetime.now()

    month = str(dtn.month) if dtn.month > 9 else "0" + str(dtn.month)
    day = str(dtn.day) if dtn.day > 9 else "0" + str(dtn.day)
    hour = str(dtn.hour)
    mins = str(dtn.minute) if dtn.minute > 9 else "0" + str(dtn.minute)

    dt_str = join_char.join([str(dtn.year), month, day])
    time_str = join_char.join([hour, mins])
    return dt_str, time_str


def calc_directory(init_dir, dbg=False):
    """ Returns calculated directory structure and date as str"""
    dt_str, _ = calc_date_time()
    dt_final = os.sep.join([init_dir, dt_str])

    dbc.print_helper(("Dir: " + dt_final), dbg=dbg)
    return dt_final, dt_str

def calc_debug_levels(args_dict):
    """ Calculates debug controls common to backup utilities
        RETURNS :: dbg, print_dbg
    """
    print_dbg = True
    if "debug_file" in args_dict.keys() and args_dict["debug_file"] is not None:
        dbg = dbc.debug_control(args_dict["debug_file"], debug_level=1)
    else:
        dbg = args_dict["verbose"] > 0
        print_dbg = args_dict["verbose"] > 0

    return dbg, print_dbg

def apply_rsync(init_base_dir, init_rslt_dir, itm, dbg=False):
    """ copies files from src (init_base_dir) to dest (init_rslt_dir)
    """
    print_dbg = dbc.test_dbg(dbg)

    rsync_list = [
        "rsync",
        "-vuogptr",
        "--info=SKIP,STATS",
        "--exclude=.*.sw[op] --exclude=*.pyc",
        (init_base_dir + os.sep),
        init_rslt_dir,
    ]
    base_str = "".join(["RSYNC: ", itm, "--", " ".join(rsync_list), os.linesep])
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
