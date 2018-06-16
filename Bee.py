#!/Users/TiM/.pyenv/versions/django_test/bin/python
# -*- coding: utf8 -*-

import pymysql
import subprocess
import logging
import fire
import json

from prettytable import PrettyTable

class Fandb:
    def __init__(self, host, port, user, password, db, charset='utf8mb4'):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                    password=self.password, db=self.db, charset=self.charset)
        self.cursor = self.conn.cursor()
        self.diccursor = self.conn.cursor(pymysql.cursors.DictCursor)
    def dml(self, sql, val=None):
        if val:
            self.cursor.execute(sql, val)
        else:
            self.cursor.execute(sql)
    def version(self):
        self.cursor.execute('select version()')
        return self.cursor.fetchone()
    def dql(self, sql, val=None):
        if val:
            self.cursor.execute(sql, val)
        else:
            self.cursor.execute(sql)
        return self.cursor.fetchall()
    def commit(self):
        self.conn.commit()
    def close(self):
        self.cursor.close()
        self.diccursor.close()
        self.conn.close()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()
        return

class Bee:
    def __init__(self, host, port, user, password, sleep, *args):
        self.host = host
        self.port = str(port)
        self.password = password
        self.user = user
        self.sleep = str(sleep)
        self.args = args
    def add_semicolon(self, _str):
        if not _str.endswith(';'):
            _str += ';'
        return _str
    def file_to_string(self, file):
        with open(file, 'r') as sqlfile:
            sql_list = [ self.add_semicolon(x.strip()) for x in sqlfile.readlines() ]
        return ''.join(sql_list)
    def magic_sql(self, orig_sql):
        assert isinstance('orig_sql', str), "Query must be string"
        dash = '--'
        host = dash + 'host=' + self.host + ';'
        port = dash + 'port=' + self.port + ';'
        password = dash + 'password=' + self.password + ';'
        user = dash + 'user=' + self.user + ';'
        sleep = dash + 'sleep=' + self.sleep + ';'
        if self.args:
            magic_args = [ '--' + x + ';' for x in self.args ]
        else:
            magic_args = []
        magic_sql = '/*' + host + port + password + user + sleep + ''.join(magic_args) + '*/' + 'inception_magic_start;' + self.add_semicolon(orig_sql) + 'inception_magic_commit;'
        return magic_sql
    # def _subprocess(self, cmd):
    #     child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #     while child.poll() == None:
    #         stdout_line = child.stdout.readline().strip()
    #         if stdout_line:
    #             logging.info(stdout_line)
    #     logging.info(child.stdout.read().strip())
    #     result = child.communicate()[0].strip()
    #     state = child.returncode
    #     return state, result
    def run_inception(self, conn, sql):
        res = conn.dql(sql)
        return res
    def pretty_table(self, inception_result):
        title = (
            'id', 'stage', 'errlevel', 'stafestatus', 'errormessage', 'sql',
            'affected_rows', 'sequence', 'backup_dbname','execute_time(s)', 'SQLSHA1'
        )
        x = PrettyTable(title)
        for row in inception_result:
            x.add_row(row)
        print()
        print(x)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return


def get_args(**inception_args_here):
    global arguments
    arguments = inception_args_here
    if arguments.get('verbose',False):
        global verbose
        verbose = True
        cut_off_line = '*'*len(repr(inception_args_here))
        print(cut_off_line)
        print(inception_args_here)
        print(cut_off_line)

def show_info(arguments, Bee_version = 'Bee 0.1.0'):
    if arguments.get('help',False) is True:
        print(_doc)
    if arguments.get('version',False):
        print(Bee_version)


if __name__ == '__main__':
    _doc = """
Usage:
        Bee.py PUT_INCEPTION_ARS_HERE (--sql=<sql> | --file=<sqlfile>) [--log-file=<log>]
        Bee.py --help
        Bee.py --version
Options:
        --help                                 查看帮助信息.
        --version                              查看版本信息.
        --verbose                              输出更多信息
        --sql=<sql>                            传递给Inception的SQL语句.
        --file=<sqlfile>                       传递给Inception的包含SQL语句的文件.
        --log-file=<log>                       log file [default: ./Bee.log]
more help information in:
https://github.com/Fanduzi
            """
    inception_host = '192.168.2.54'
    inception_port = 6669
    inception_user = ''
    inception_passwd = ''
    inception_db = ''

    arguments = {}
    verbose = False
    fire.Fire(get_args)
    show_info(arguments)

    log_file = arguments.get('log-file',False) if arguments.get('log-file',False) else 'Bee.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_file,
                        filemode='a')
    db_host = arguments['host']
    db_port = arguments['port']
    db_user = arguments['user']
    db_password = arguments['password']
    sleep = arguments.get('sleep') if arguments.get('sleep',False) else 0
    orig_sql = arguments.get('sql') if not arguments.get('file',False) else arguments.get('file')
    endisable_list = [ x for x in arguments.keys() if x.startswith('enable') or x.startswith('disable') and arguments[x] is True ]
    with Bee(db_host, db_port, db_user, db_password, sleep, *endisable_list) as _Bee:
        magic_sql = _Bee.magic_sql(orig_sql)
        with Fandb(inception_host, inception_port, inception_user, inception_passwd, inception_db) as _Fandb:
            res = _Bee.run_inception(_Fandb, magic_sql)
            if verbose is True:
                print(res)
            if not arguments.get('enable_query_print',False):
                _Bee.pretty_table(res)
            else:
                dicts = eval(res[0][3])
                json_dicts = json.dumps(dicts, indent=4)
                print(json_dicts)





