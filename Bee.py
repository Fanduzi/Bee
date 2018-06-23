#!/Users/TiM/.pyenv/versions/django_test/bin/python
# -*- coding: utf8 -*-

import sys
import fire
import json
import pymysql
import logging

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
    def stdin_to_string(self):
        stdin_sql = sys.stdin.readlines()
        sql_list = [self.add_semicolon(x.strip()) for x in stdin_sql]
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
    def run_inception(self, conn, sql):
        res = conn.dql(sql)
        return list(map(list,res))
    def get_rollback_sql(self, conn, sequence, backup_dbname):
        res = None
        if backup_dbname != 'None':
            sql_table_name = "select tablename from {}.`$_$Inception_backup_information$_$` where opid_time={}".format(backup_dbname, sequence)
            res = conn.dql(sql_table_name)
        if res:
            table_name = res[0][0]
            sql_rollback = "select rollback_statement from {}.{} where opid_time={}".format(backup_dbname, table_name, sequence)
            res = conn.dql(sql_rollback)
            rollback_statement = res[0][0] if res else ''
        else:
            rollback_statement = ''
        return rollback_statement
    def pretty_table(self, inception_result):
        title =(
            'id', 'stage', 'errlevel', 'stafestatus', 'errormessage', 'sql',
            'affected_rows', 'sequence', 'backup_dbname','execute_time',
            'SQLSHA1', 'rollback_statement'
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
    if 'verbose' in arguments:
        global verbose
        verbose = True
        cut_off_line = '*'*len(repr(inception_args_here))
        print(cut_off_line)
        print(inception_args_here)
        print(cut_off_line)

def show_info(arguments, Bee_version = 'Bee 0.2.0'):
    if arguments.get('help',False) is True:
        print(_doc)
    if 'version' in arguments:
        print(Bee_version)


def is_queryable(conn, db_name, table_name, field):
    sql = """select count(id)
              from fandb.db_query_blacklist
             where database_name_alias='{}' and table_name='{}' and column_name='{}' and is_queryable=0
          """.format(db_name, table_name, field)
    #print(sql)
    res = conn.dql(sql)[0][0]
    return res


def get_col_recursive(conn, res_dict):
    for item in res_dict["select_list"]:
        if 'subselect' in item:
            """
            标量子查询, 需要递归
            """
            new_item = item['subselect']
            get_col_recursive(conn, new_item)
        else:
            field = item['field']
            if 'table' not in item:
                table_name = res_dict['table_ref'][0]['table']
                db_name = res_dict['table_ref'][0]['db']
            else:
                table_name = item['table']
                db_name = item['db']
            print('''Selected columns:
                {db_name}.{table_name}.{field}'''.format(db_name=db_name, table_name=table_name, field=field))
            res = is_queryable(conn, db_name, table_name, field)
            if res != 0:
                print('{db}.{table_name}.{field} is unqueryable!'.format(db=db_name, table_name=table_name, field=field))






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

    log_file = arguments.get('log-file') if 'log-file' in arguments else 'Bee.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=log_file,
                        filemode='a')
    db_host = arguments['host']
    db_port = arguments['port']
    db_user = arguments['user']
    db_password = arguments['password']
    sleep = arguments.get('sleep') if 'sleep' in arguments else 0
    endisable_list = [ x for x in arguments.keys() if x.startswith('enable') or x.startswith('disable') and arguments[x] is True ]
    with Bee(db_host, db_port, db_user, db_password, sleep, *endisable_list) as _Bee:
        if 'sql' in arguments or 'file' in arguments:
            orig_sql = arguments.get('sql') if 'file' not in arguments else _Bee.file_to_string(arguments['file'])
        else:
            orig_sql = _Bee.stdin_to_string()
        magic_sql = _Bee.magic_sql(orig_sql)
        with Fandb(inception_host, inception_port, inception_user, inception_passwd, inception_db) as _Fandb:
            res = _Bee.run_inception(_Fandb, magic_sql)
            if verbose is True:
                print(res)
            if 'enable_query_print' not in arguments:
                with Fandb(db_host, db_port, db_user, db_password, '') as backupdb_conn:
                    for row in res:
                        rollback_statement = _Bee.get_rollback_sql(backupdb_conn, row[7], row[8])
                        row.append(rollback_statement)
                _Bee.pretty_table(res)
            else:
                res_dict = eval(res[0][3])
                json_dicts = json.dumps(res_dict, indent=4)
                print(json_dicts)
                with Fandb(db_host, db_port, db_user, db_password, '') as conn_query_blacklist:
                    get_col_recursive(conn_query_blacklist, res_dict)

