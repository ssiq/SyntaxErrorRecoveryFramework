import os

scrapyOJ_DB_PATH = r'/home/lf/new_disk/data_store/codeforces/scrapyOJ.db'

ROOT_PATH = r'/home/lf/Project/SyntaxErrorRecoveryFramework'
DATA_PATH = os.path.join(ROOT_PATH, 'data')


verdict = {'OK': 1, 'REJECTED': 2, 'WRONG_ANSWER': 3, 'RUNTIME_ERROR': 4, 'TIME_LIMIT_EXCEEDED': 5, 'MEMORY_LIMIT_EXCEEDED': 6,
           'COMPILATION_ERROR': 7, 'CHALLENGED': 8, 'FAILED': 9, 'PARTIAL': 10, 'PRESENTATION_ERROR': 11, 'IDLENESS_LIMIT_EXCEEDED': 12,
           'SECURITY_VIOLATED': 13, 'CRASHED': 14, 'INPUT_PREPARATION_CRASHED': 15, 'SKIPPED': 16, 'TESTING': 17, 'SUBMITTED': 18}
langdict = {'GNU C': 1, 'GNU C11': 2, 'GNU C++': 3, 'GNU C++11': 4, 'GNU C++14': 5,
            'MS C++': 6, 'Mono C#': 7, 'MS C#': 8, 'D': 9, 'Go': 10,
            'Haskell': 11, 'Java 8': 12, 'Kotlin': 13, 'Ocaml': 14, 'Delphi': 15,
            'FPC': 16, 'Perl': 17, 'PHP': 18, 'Python 2': 19, 'Python 3': 20,
            'PyPy 2': 21, 'PyPy 3': 22, 'Ruby': 23, 'Rust': 24, 'Scala': 25,
            'JavaScript': 26}
