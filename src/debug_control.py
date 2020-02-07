""" File containing the new debugging object. This debugging object cab wright stdout or filename
        and incorporates time logging of writes.
"""
#!/usr/bin/python3
import datetime as dt
import os


class debug_control(object):
    """ debug_control -- object wrapping debug output
    """

    def __init__(self, filename=None, debug_level=0, time_str="%Y/%m/%d %H:%M:%S"):
        self.start = dt.datetime.now()
        self.orig = self.start
        self.curr = self.start
        self.filename = filename
        self.reporting_level = debug_level
        self.time_str = time_str
        if self.reporting_level > 0 and filename is not None:
            self.handle = open(self.filename, "w", encoding="utf-8")
        else:
            if self.reporting_level > 0:
                print("reporting level must be positive & file not None")

    def write(self, string):
        """ Simple write method to--string appended w/ datetime & new line seperator """
        if self.handle.closed:
            print("File closed")
        else:
            self.curr = dt.datetime.now()
            string = "".join(
                [string, "-- ", self.curr.strftime(self.time_str), os.linesep]
            )
            self.handle.writelines(string)

    def write_stdout(self, processname, out=None):
        ''' Writes tyo std out takes processname & out '''
        if out is not None:
            init = out.decode("UTF-8").split("\n")
            self.curr = dt.datetime.now()
            base_str = "".join(
                [
                    processname,
                    " (stdout) -- ",
                    str(len(init)),
                    os.linesep,
                    self.curr.strftime(self.time_str),
                    os.linesep,
                ]
            )
            self.handle.writelines(base_str)
            for itm in init:
                itm2 = itm + os.linesep
                self.handle.writelines(itm2)

    def write_stderr(self, processname, out=None):
        """ Attmepts to capture standard error and write stream """
        if out is not None:
            self.curr = dt.datetime.now()
            base_str = " ".join(
                [
                    processname,
                    "(stderr) --",
                    out.decode("UTF-8"),
                    os.linesep,
                    self.curr.strftime(self.time_str),
                    os.linesep
                ]
            )
            self.handle.writelines(base_str)

    def close(self):
        """ closes open file handle and applies closing message"""
        base_time = dt.datetime.now()
        base_diff = base_time - self.orig
        base_str = " ".join(
            [
                "Finishing (",
                self.orig.strftime(self.time_str),
                ") elapsed time (min : sec)",
                str(base_diff.seconds // 60),
                ": ",
                str(base_diff.seconds % 60),
            ]
        )
        self.write(base_str)

        if self.handle.closed:
            if self.reporting_level > 0:
                self.write("File is closed")
        else:
            self.handle.close()

    def __del__(self):
        if not self.handle.closed:
            self.handle.close()

def test_dbg(dbg):
    """ Simple function to test debug status"""
    return (isinstance(dbg, bool) and dbg) or (
        isinstance(dbg, debug_control) and dbg.reporting_level > 0
    )


def print_helper(base_str, dbg):
    """ print helper applied to test dbg type and take correct print action """
    print_dbg = test_dbg(dbg)
    if print_dbg:
        if isinstance(dbg, bool):
            print(
                "  ".join([dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), base_str])
            )
        else:
            dbg.write(base_str)

def print_helper_tuple(init_str, base_str, base_tuple=None, dbg=None):
    """ print helper applied to test dbg type and take correct print action """
    if dbg is not None:
        print_dbg = test_dbg(dbg)
    else:
        print_dbg = False

    if print_dbg:
        if base_tuple is not None and isinstance(base_tuple, (tuple, dict)):
            if isinstance(base_str, tuple):
                fnl_str = "".join(base_str)
            elif isinstance(base_str, str):
                fnl_str = base_str

            fnl_str = fnl_str % base_tuple
            fnl_str = init_str + fnl_str
            if isinstance(dbg, bool):
                print(
                    "  ".join([dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), fnl_str])
                )
            else:
                dbg.write(fnl_str)
        else:
            if isinstance(base_str, tuple):
                base_str = "".join(base_str)
            print_helper("".join([init_str, base_str]), dbg)

def error_helper(pred, stderr=None, post=None, dbg=False):
    """
    pred predicate e.g. Diff Error
    stderr -- expects in bytew to be decoded from subp.stderr
    post -- defaults to None (& excluded)
    """
    print_dbg = (isinstance(dbg, bool) and dbg) or (
        isinstance(dbg, debug_control) and dbg.reporting_level > 0
    )

    if print_dbg:
        if isinstance(dbg, bool):
            base_time_str = dt.datetime.now()
            base_list = [pred]
            if stderr is not None:
                base_list.append(stderr.decode("UTF-8"))

            if post is not None:
                base_list.append(post)
            base_list.append(base_time_str.strftime("%Y/%m/%d %H:%M:%S"))
            print(" ".join(base_list))
        else:
            dbg.write_stderr(pred, stderr)
