from common.constants import ACTUAL_C_ERROR_RECORDS, CPP_TESTCASE_ERROR_RECORDS

CREATE_ACTUAL_C_ERROR_RECORDS = r'''CREATE TABLE IF NOT EXISTS actual_c_error_records (
  id TEXT PRIMARY KEY,
  submit_url TEXT,
  problem_id TEXT,
  user_id TEXT,
  problem_user_id TEXT,
  code TEXT,
  gcc_compile_result INTEGER, 
  pycparser_result INTEGER, 
  similar_code TEXT DEFAULT '', 
  modify_action_list TEXT DEFAULT '', 
  distance INTEGER DEFAULT -1
)'''

CREATE_CPP_TESTCASE_ERROR_RECORDS = r'''CREATE TABLE IF NOT EXISTS cpp_testcase_error_records (
  id TEXT PRIMARY KEY,
  submit_url TEXT,
  problem_id TEXT,
  user_id TEXT,
  problem_user_id TEXT,
  code TEXT,
  gcc_compile_result INTEGER, 
  similar_code TEXT DEFAULT '', 
  modify_action_list TEXT DEFAULT '', 
  distance INTEGER DEFAULT -1, 
  testcase TEXT DEFAULT ''
)'''

FIND_CPP_TESTCASE_DISTINCT_PROBLEM_USER_ID = r'''SELECT DISTINCT problem_user_id from cpp_testcase_error_records'''

INSERT_IGNORE_ACTUAL_C_ERROR_RECORDS = r'''INSERT OR IGNORE INTO actual_c_error_records (id, submit_url, problem_id, user_id, problem_user_id, code, gcc_compile_result, pycparser_result, similar_code, modify_action_list, distance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
INSERT_IGNORE_CPP_TESTCASE_ERROR_RECORDS = r'''INSERT OR IGNORE INTO cpp_testcase_error_records (id, submit_url, problem_id, user_id, problem_user_id, code, gcc_compile_result, similar_code, modify_action_list, distance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''


sql_dict = {ACTUAL_C_ERROR_RECORDS: {'create': CREATE_ACTUAL_C_ERROR_RECORDS,
                                     'insert_ignore': INSERT_IGNORE_ACTUAL_C_ERROR_RECORDS, },
            CPP_TESTCASE_ERROR_RECORDS: {'create': CREATE_CPP_TESTCASE_ERROR_RECORDS,
                                         'insert_ignore': INSERT_IGNORE_CPP_TESTCASE_ERROR_RECORDS,
                                         'find_distinct_problem_user_id': FIND_CPP_TESTCASE_DISTINCT_PROBLEM_USER_ID}
            }

