""" Class wrapper around the python interface to mysql database """
#!/usr/bin/python3
# import MySQLdb as mysqldb
import mysql.connector as mysqldb


class mysql_db_class(object):
    """ Simple class wrapping access to mysql database """

    def __init__(self, path="/home/spennington/.mylogin.cnf", group="remote", password=None,
                 host="localhost", user="spennington", db="jobsearch"):
        self.connection = None
        self.host = host
        self.user = user
        # self.password = password
        self.database = db

        if password is None and path is not None:
            self.connection = mysqldb.connect(option_files=path, option_groups=group,
                                              use_unicode=True, charset="utf8",
                                              collation="utf8_general_ci", db=self.database)
        else:
            self.connection = mysqldb.connect(
                host=self.host, user=self.user, password=password, db=self.database
            )

        self.cursor = self.connection.cursor()

        if self.database is not None:
            self.cursor.execute("USE " + self.database + ";")

    def insert(self, query):
        """ Simple insert query -- with roll back in case of failure , returns 1
            in case of success
        """
        success = 1
        try:
            self.cursor.execute(query)
            self.connection.commit()
            success = 0
        except:
            self.connection.rollback()

        return success

    def insert_mutiple_rows(self, query, vals):
        """ Simple insert many rows query -- with roll back in case of failure , returns 1
            in case of success
        """
        success = 1
        try:
            self.cursor.executemany(query, vals)
            self.connection.commit()
            success = 0
        except:
            self.connection.rollback()

        return success

    def update(self, query):
        """ Simple update query -- with roll back in case of failure"""
        success = 1
        try:
            self.cursor.execute(query)
            self.connection.commit()
            success = 0
        except:
            self.connection.rollback()

        return success

    def query(self, query):
        """ Select query fetch -- applies MySQLCursorDict to cursor"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)

        return cursor.fetchall()

    def execute_stored_procedure(self, sp_name, sp_args_list):
        """ Call stored procedure from mysql"""
        success = 1
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc(sp_name, sp_args_list)
            # self.connection.commit()
            success = 0
        except:
            self.connection.rollback()

        return success

    def __del__(self):
        if self.connection:
            self.connection.close()
