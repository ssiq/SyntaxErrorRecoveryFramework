import sqlite3
import pandas as pd

from common.constants import PROBLEM_TESTCASE, COMPILE_SUCCESS_DATA_DBPATH, TRAIN_DATA_DBPATH
from config import scrapyOJ_path
from database.database_util import create_table, insert_items


scrapy_con = sqlite3.connect(scrapyOJ_path)

count = 0
def filter_one_ok_records(problem_id, key='problem_name'):
    # problem_id = one['problem_name']
    global count
    count += 1
    if count % 1 == 0:
        print('count : {}, {}'.format(count, problem_id))
    cur = scrapy_con.cursor()
    cmd = "select * from submit where status='OK' and {}='{}' limit 1, 1;".format(key, problem_id)
    cur.execute(cmd)
    res = cur.fetchall()
    if len(res) == 0:
        return None
    return res[0]


def change_to_save_order(one):
    save_one = [one[0], one[1], one[5], one[3], one[7]+'_'+one[3], one[14]]
    return save_one


def resave_problem_in_submit_records_form(problem_id_list=None):
    if problem_id_list is None:
        cpp_testcase_con = sqlite3.connect(TRAIN_DATA_DBPATH)
        problem_id_list = pd.read_sql('select distinct problem_id from cpp_testcase_error_records where distance!=-1', cpp_testcase_con)['problem_id'].tolist()
    # problem_id_list = problem_id_list[:100]
    print('total_problem: {}'.format(len(problem_id_list)))
    ok_record_list = [filter_one_ok_records(i, 'problem_id') for i in problem_id_list]
    read_list = list(filter(lambda x: x is not None, ok_record_list))
    print('effect_problem: {}'.format(len(read_list)))

    # problem_df = pd.read_sql('select * from problem', scrapy_con)
    # # problem_df = problem_df.sample(100)
    # print('total_problem: {}'.format(len(problem_df)))
    # problem_df['ok_record'] = problem_df['problem_name'].map(filter_one_ok_records)
    # problem_df = problem_df[problem_df['ok_record'].map(lambda x: x is not None)]
    # print('effect_problem: {}'.format(len(problem_df)))
    # read_list = problem_df['ok_record'].tolist()

    save_list = [change_to_save_order(r) for r in read_list]

    create_table('data/problem_testcase_effect_cpp.db', PROBLEM_TESTCASE)
    insert_items('data/problem_testcase_effect_cpp.db', PROBLEM_TESTCASE, save_list)


if __name__ == '__main__':
    problem_id_list = ['107532', '106951', '85240', '41578', '41577', '41576', '41575', '41574', '41573', '2110',
                       '120316', '120315', '120314', '120313', '120312', '120760']
    resave_problem_in_submit_records_form(problem_id_list)
