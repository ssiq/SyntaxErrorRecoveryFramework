import sqlite3
import pandas as pd

from common.constants import verdict, langdict, scrapyOJ_DB_PATH


def merge_and_deal_submit_table(problems_df, submit_df):
    submit_joined_df = submit_df.join(problems_df.set_index('problem_name'), on='problem_name')
    submit_joined_df['time'] = submit_joined_df['time'].str.replace('ms', '').astype('int')
    submit_joined_df['memory'] = submit_joined_df['memory'].str.replace('KB', '').astype('int')
    submit_joined_df['submit_time'] = pd.to_datetime(submit_joined_df['submit_time'])
    submit_joined_df['tags'] = submit_joined_df['tags'].str.split(':')
    submit_joined_df['code'] = submit_joined_df['code'].str.slice(1, -1)
    submit_joined_df['language'] = submit_joined_df['language'].replace(langdict)
    submit_joined_df['status'] = submit_joined_df['status'].replace(verdict)
    return submit_joined_df


def read_all_submit_data(conn: sqlite3.Connection) -> pd.DataFrame:
    problems_df = pd.read_sql('select problem_name, tags from {}'.format('problem'), conn)
    submit_df = pd.read_sql('select * from {}'.format('submit'), conn)
    submit_joined_df = merge_and_deal_submit_table(problems_df, submit_df)
    return submit_joined_df


def read_all_c_data(conn):
    problems_df = pd.read_sql('select problem_name, tags from {}'.format('problem'), conn)
    submit_df = pd.read_sql('select * from {} where language="GNU C"'.format('submit'), conn)
    submit_joined_df = merge_and_deal_submit_table(problems_df, submit_df)
    return submit_joined_df


def read_data(conn, table, condition=None):
    extra_filter = ''
    note = '"'
    if condition is not None:
        extra_filter += ' where '
        condition_str = ['{}={}{}{}'.format(key, note, value, note) if isinstance(str, value)
                         else '{}={}'.format(key, value) for key, value in condition.items()]
        extra_filter += (' and '.join(condition_str))
    sql = 'select * from {} {}'.format(table, extra_filter)
    data_df = pd.read_sql(sql, conn)
    print('read data sql statment: {}. length:{}'.format(sql, len(data_df.index)))
    return data_df


def read_all_c_records():
    conn = sqlite3.connect("file:{}?mode=ro".format(scrapyOJ_DB_PATH), uri=True)
    data_df = read_all_c_data(conn)
    return data_df


def read_all_submit_records():
    conn = sqlite3.connect("file:{}?mode=ro".format(scrapyOJ_DB_PATH), uri=True)
    data_df = read_all_submit_data(conn)
    return data_df


