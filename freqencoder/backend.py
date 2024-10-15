import os
import glob
import tempfile
from torch.utils.cpp_extension import load

_src_path = os.path.dirname(os.path.abspath(__file__))

nvcc_flags = [
    '-O3', '-std=c++14',
    '-U__CUDA_NO_HALF_OPERATORS__', '-U__CUDA_NO_HALF_CONVERSIONS__', '-U__CUDA_NO_HALF2_OPERATORS__',
    '-use_fast_math'
]

if os.name == "posix":
    # 适用于 Linux 的 c_flags
    c_flags = ['-O3', '-std=c++14', '-Wl,-E', '-ldl', '-DLUA_COMPAT_5_3', '-DLUA_USE_LINUX']
elif os.name == "nt":
    # Windows 不需要 -Wl, -E, 和 -ldl
    c_flags = ['/O2', '/std:c++17', '-DLUA_COMPAT_5_3', '-DLUA_USE_WINDOWS']  # 修改为 -DLUA_USE_WINDOWS

    # find cl.exe
    def find_cl_path():
        import glob
        for program_files in [r"C:\\Program Files (x86)", r"C:\\Program Files"]:
            for edition in ["Enterprise", "Professional", "BuildTools", "Community"]:
                paths = sorted(glob.glob(r"%s\\Microsoft Visual Studio\\*\\%s\\VC\\Tools\\MSVC\\*\\bin\\Hostx64\\x64" % (program_files, edition)), reverse=True)
                if paths:
                    return paths[0]

    # If cl.exe is not on path, try to find it.
    if os.system("where cl.exe >nul 2>nul") != 0:
        cl_path = find_cl_path()
        if cl_path is None:
            raise RuntimeError("Could not locate a supported Microsoft Visual C++ installation")
        os.environ["PATH"] += ";" + cl_path

# 手动指定的源文件列表
manual_sources = [os.path.join(_src_path, 'src', f) for f in [
    # 'freqencoder.cu',
    'freqencoder.cpp',
    'bindings.cpp',
]]

# 动态获取 src/lua467 目录下的所有 .cpp 和 .cu 文件
lua467_sources = glob.glob(os.path.join(_src_path, 'src', 'lua547', '*.cpp')) + \
                 glob.glob(os.path.join(_src_path, 'src', 'lua547', '*.c')) + \
                 glob.glob(os.path.join(_src_path, 'src', 'lua547', '*.cu'))

# 合并手动指定的文件和 lua467 目录下的所有文件
all_sources = manual_sources + lua467_sources

# with tempfile.TemporaryDirectory() as build_dir:
_backend = load(name='_freqencoder_v6',
                extra_cflags=c_flags,
                # extra_cuda_cflags=nvcc_flags,
                build_directory="/content/tmp2/",
                sources=all_sources,
                # build_directory=build_dir,  # 使用临时编译目录确保每次都重新编译
                verbose=True
                )

# 使用临时目录来确保每次都进行重新编译
# with tempfile.TemporaryDirectory() as build_dir:
#     _backend = load(name='_freqencoder',
#                     extra_cflags=c_flags,
#                     # extra_cuda_cflags=nvcc_flags,
#                     # build_directory="/content/tmp1/",
#                     sources=all_sources,
#                     build_directory=build_dir,  # 使用临时编译目录确保每次都重新编译
#                     verbose=True
#                     )

__all__ = ['_backend']