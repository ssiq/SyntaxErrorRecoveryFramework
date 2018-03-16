import unittest

from error_recovery.marked_code import MarkedCode


class TestMarkedCode(unittest.TestCase):
    def setUp(self):
        headers = ['int add(int a, int b);']
        header_names = ['my_math.h']
        sources = [r"""#include<stdio.h>
#include"my_math.h"

int main()
{
    int a=1, b=2;
    printf("%d\n", add(a, b));
}"""]
        source_names = ['main.c']
        self.mark_code = MarkedCode(headers, header_names, sources, source_names)

    def test__str__(self):
        expected_result = r"""# 1 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\tmp\\tmp_code_preprocess\\source\\main.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\tmp\\tmp_code_preprocess\\source\\main.c"
# 1 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\pycparser\\utils\\fake_libc_include/stdio.h" 1
# 1 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\pycparser\\utils\\fake_libc_include/_fake_defines.h" 1
# 41 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\pycparser\\utils\\fake_libc_include/_fake_defines.h"
typedef int va_list;
# 2 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\pycparser\\utils\\fake_libc_include/stdio.h" 2
# 1 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\pycparser\\utils\\fake_libc_include/_fake_typedefs.h" 1



typedef int size_t;
typedef int __builtin_va_list;
typedef int __gnuc_va_list;
typedef int __int8_t;
typedef int __uint8_t;
typedef int __int16_t;
typedef int __uint16_t;
typedef int __int_least16_t;
typedef int __uint_least16_t;
typedef int __int32_t;
typedef int __uint32_t;
typedef int __int64_t;
typedef int __uint64_t;
typedef int __int_least32_t;
typedef int __uint_least32_t;
typedef int __s8;
typedef int __u8;
typedef int __s16;
typedef int __u16;
typedef int __s32;
typedef int __u32;
typedef int __s64;
typedef int __u64;
typedef int _LOCK_T;
typedef int _LOCK_RECURSIVE_T;
typedef int _off_t;
typedef int __dev_t;
typedef int __uid_t;
typedef int __gid_t;
typedef int _off64_t;
typedef int _fpos_t;
typedef int _ssize_t;
typedef int wint_t;
typedef int _mbstate_t;
typedef int _flock_t;
typedef int _iconv_t;
typedef int __ULong;
typedef int __FILE;
typedef int ptrdiff_t;
typedef int wchar_t;
typedef int __off_t;
typedef int __pid_t;
typedef int __loff_t;
typedef int u_char;
typedef int u_short;
typedef int u_int;
typedef int u_long;
typedef int ushort;
typedef int uint;
typedef int clock_t;
typedef int time_t;
typedef int daddr_t;
typedef int caddr_t;
typedef int ino_t;
typedef int off_t;
typedef int dev_t;
typedef int uid_t;
typedef int gid_t;
typedef int pid_t;
typedef int key_t;
typedef int ssize_t;
typedef int mode_t;
typedef int nlink_t;
typedef int fd_mask;
typedef int _types_fd_set;
typedef int clockid_t;
typedef int timer_t;
typedef int useconds_t;
typedef int suseconds_t;
typedef int FILE;
typedef int fpos_t;
typedef int cookie_read_function_t;
typedef int cookie_write_function_t;
typedef int cookie_seek_function_t;
typedef int cookie_close_function_t;
typedef int cookie_io_functions_t;
typedef int div_t;
typedef int ldiv_t;
typedef int lldiv_t;
typedef int sigset_t;
typedef int __sigset_t;
typedef int _sig_func_ptr;
typedef int sig_atomic_t;
typedef int __tzrule_type;
typedef int __tzinfo_type;
typedef int mbstate_t;
typedef int sem_t;
typedef int pthread_t;
typedef int pthread_attr_t;
typedef int pthread_mutex_t;
typedef int pthread_mutexattr_t;
typedef int pthread_cond_t;
typedef int pthread_condattr_t;
typedef int pthread_key_t;
typedef int pthread_once_t;
typedef int pthread_rwlock_t;
typedef int pthread_rwlockattr_t;
typedef int pthread_spinlock_t;
typedef int pthread_barrier_t;
typedef int pthread_barrierattr_t;
typedef int jmp_buf;
typedef int rlim_t;
typedef int sa_family_t;
typedef int sigjmp_buf;
typedef int stack_t;
typedef int siginfo_t;
typedef int z_stream;


typedef int int8_t;
typedef int uint8_t;
typedef int int16_t;
typedef int uint16_t;
typedef int int32_t;
typedef int uint32_t;
typedef int int64_t;
typedef int uint64_t;


typedef int int_least8_t;
typedef int uint_least8_t;
typedef int int_least16_t;
typedef int uint_least16_t;
typedef int int_least32_t;
typedef int uint_least32_t;
typedef int int_least64_t;
typedef int uint_least64_t;


typedef int int_fast8_t;
typedef int uint_fast8_t;
typedef int int_fast16_t;
typedef int uint_fast16_t;
typedef int int_fast32_t;
typedef int uint_fast32_t;
typedef int int_fast64_t;
typedef int uint_fast64_t;


typedef int intptr_t;
typedef int uintptr_t;


typedef int intmax_t;
typedef int uintmax_t;


typedef _Bool bool;

typedef int va_list;


typedef void* MirEGLNativeWindowType;
typedef void* MirEGLNativeDisplayType;
typedef struct MirConnection MirConnection;
typedef struct MirSurface MirSurface;
typedef struct MirSurfaceSpec MirSurfaceSpec;
typedef struct MirScreencast MirScreencast;
typedef struct MirPromptSession MirPromptSession;
typedef struct MirBufferStream MirBufferStream;
typedef struct MirPersistentId MirPersistentId;
typedef struct MirBlob MirBlob;
typedef struct MirDisplayConfig MirDisplayConfig;


typedef struct xcb_connection_t xcb_connection_t;
typedef uint32_t xcb_window_t;
typedef uint32_t xcb_visualid_t;
# 3 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\pycparser\\utils\\fake_libc_include/stdio.h" 2
# 2 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\tmp\\tmp_code_preprocess\\source\\main.c" 2
# 1 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\tmp\\tmp_code_preprocess\\header/my_math.h" 1
int add(int a, int b);
# 3 "D:\\Machine Learning\\SyntaxErrorRecoveryFramework\\tmp\\tmp_code_preprocess\\source\\main.c" 2

int main()
{
    int a=1, b=2;
    printf("%d\n", add(a, b));
}
"""
        self.assertEqual(str(self.mark_code), expected_result, 'the __str__ function of MarkedCode failed')

    def test_is_in_system_header(self):
        self.assertTrue(self.mark_code.is_in_system_header(17), "This line should be in the system header")
        self.assertTrue(self.mark_code.is_in_system_header(8), "This line should be in the system header")
        self.assertTrue(not self.mark_code.is_in_system_header(185), "This line should not be in the system header")
        self.assertTrue(not self.mark_code.is_in_system_header(190), "This line should not be in the system header")

