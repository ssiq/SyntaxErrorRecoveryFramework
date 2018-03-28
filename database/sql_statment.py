from common.constants import ACTUAL_C_ERROR_RECORDS

CREATE_ACTUAL_C_ERROR_RECORDS = r'''CREATE TABLE IF NOT EXISTS actual_c_error_records (
  id TEXT PRIMARY KEY,
  submit_id TEXT,
  problem_id TEXT,
  user_id TEXT,
  problem_user_id TEXT,
  code TEXT,
  gcc_compile_result INTEGER, 
  pycparser_result INTEGER, 
  similar_code TEXT DEFAULT '', 
  modify_action_list TEXT DEFAULT '', 
  error_to_ac_action_list TEXT DEFAULT '', 
  distance INTEGER DEFAULT -1
)'''

INSERT_IGNORE_ACTUAL_C_ERROR_RECORDS = r'''INSERT OR IGNORE INTO fake_code_records (id, submit_id, problem_id, user_id, problem_user_id, code, gcc_compile_result, pycparser_result, similar_code, modify_action_list, error_to_ac_action_list, distance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''


sql_dict = {ACTUAL_C_ERROR_RECORDS: {'create': CREATE_ACTUAL_C_ERROR_RECORDS,
                                     'insert_ignore': INSERT_IGNORE_ACTUAL_C_ERROR_RECORDS, },
            }

