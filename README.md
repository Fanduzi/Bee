# Bee

```
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
```

Example
```
#python Bee.py --user=innet --password=fanboshi --host=192.168.2.54 --port=3308 --enable-check --sql="update fandb.fan set uname = 6 where id>19;select * from fandb.fan;"

+----+---------+----------+-----------------+-----------------------------------------------+--------------------------------------------+---------------+----------+-------------------------+-----------------+---------+
| id |  stage  | errlevel |   stafestatus   |                  errormessage                 |                    sql                     | affected_rows | sequence |      backup_dbname      | execute_time(s) | SQLSHA1 |
+----+---------+----------+-----------------+-----------------------------------------------+--------------------------------------------+---------------+----------+-------------------------+-----------------+---------+
| 1  | CHECKED |    0     | Audit completed |                      None                     | update fandb.fan set uname = 6 where id>19 |       2       | '0_0_0'  | 192_168_2_54_3308_fandb |        0        |         |
| 2  | CHECKED |    1     | Audit completed | set the where condition for select statement. |          select * from fandb.fan           |       0       | '0_0_1'  |           None          |        0        |         |
|    |         |          |                 |        Select only star is not allowed.       |                                            |               |          |                         |                 |         |
+----+---------+----------+-----------------+-----------------------------------------------+--------------------------------------------+---------------+----------+-------------------------+-----------------+-------

#python Bee.py --user=innet --password=fanboshi --host=192.168.2.54 --port=3308 --enable-execute --sql="update fandb.fan set uname = 6 where id=19"

+----+----------+----------+----------------------+--------------+--------------------------------------------+---------------+---------------------+-------------------------+-----------------+---------+
| id |  stage   | errlevel |     stafestatus      | errormessage |                    sql                     | affected_rows |       sequence      |      backup_dbname      | execute_time(s) | SQLSHA1 |
+----+----------+----------+----------------------+--------------+--------------------------------------------+---------------+---------------------+-------------------------+-----------------+---------+
| 1  | EXECUTED |    0     | Execute Successfully |     None     | update fandb.fan set uname = 6 where id=19 |       1       | '1529153422_1222_0' | 192_168_2_54_3308_fandb |      0.010      |         |
|    |          |          | Backup successfully  |              |                                            |               |                     |                         |                 |         |
+----+----------+----------+----------------------+--------------+--------------------------------------------+---------------+---------------------+-------------------------+-----------------+---------+

#python Bee.py --user=innet --password=fanboshi --host=192.168.2.54 --port=3308 --enable-query-print --sql="select uname from fandb.fan where id=19"
{
    "command": "select",
    "select_list": [
        {
            "type": "FIELD_ITEM",
            "db": "fandb",
            "table": "fan",
            "field": "uname"
        }
    ],
    "table_ref": [
        {
            "db": "fandb",
            "table": "fan"
        }
    ],
    "where": [
        {
            "type": "FUNC_ITEM",
            "func": "=",
            "args": [
                {
                    "type": "FIELD_ITEM",
                    "db": "fandb",
                    "table": "fan",
                    "field": "id"
                },
                {
                    "type": "INT_ITEM",
                    "value": "19"
                }
            ]
        }
    ]
}

#cat sqlfile.sql | python Bee.py --user=innet --password=fanboshi --host=192.168.2.54 --port=3308 --enable-check

+----+---------+----------+-----------------+-----------------------------------------------+--------------------------------------------+---------------+----------+-------------------------+-----------------+---------+
| id |  stage  | errlevel |   stafestatus   |                  errormessage                 |                    sql                     | affected_rows | sequence |      backup_dbname      | execute_time(s) | SQLSHA1 |
+----+---------+----------+-----------------+-----------------------------------------------+--------------------------------------------+---------------+----------+-------------------------+-----------------+---------+
| 1  | CHECKED |    1     | Audit completed | set the where condition for select statement. |          select * from fandb.fan           |       0       | '0_0_0'  |           None          |        0        |         |
|    |         |          |                 |        Select only star is not allowed.       |                                            |               |          |                         |                 |         |
| 2  | CHECKED |    0     | Audit completed |                      None                     | update fandb.fan set uname = 6 where id>19 |       2       | '0_0_1'  | 192_168_2_54_3308_fandb |        0        |         |
+----+---------+----------+-----------------+-----------------------------------------------+--------------------------------------------+---------------+----------+-------------------------+-----------------+---------+
```
