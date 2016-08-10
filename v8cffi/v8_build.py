# -*- coding: utf-8 -*-

import os
import platform

from cffi import FFI


SRC_PATH = os.path.join('v8cffi', 'src')

IS_MAC = platform.system() == 'Darwin'

# Need a better way to determine this, but by default homebrew
# doesn't install with icu4c, so going with that for now.
# Anyway, icu4c on homebrew is keg-only (meaning it isn't linked
# into /usr/local/lib) so the path would have to be different anyway.
HAS_ICU4C = not(IS_MAC)

if IS_MAC:
    # TODO: Don't hardcode. Better to bundle static libs?
    # ...but they're so large. Also could use more memory
    # with multiple different installs.
    STATIC_LIBS_PATH = '/usr/local/lib'
    USE_SHARED = True
else:
    STATIC_LIBS_PATH = os.path.join(SRC_PATH, 'v8', 'release')
    USE_SHARED = False


ffi = FFI()

extra_link_args = ['-ldl', '-std=c++11']

if USE_SHARED:
    extra_link_args += ['-lv8']

# TODO: Doesn't look like any of the librt functions are used anywhere anyway
if not IS_MAC:
    extra_link_args += ['-lrt']


cflags = ['-std=c++11']


if os.path.exists(os.path.join(STATIC_LIBS_PATH, 'libv8_external_snapshot.a')):
    cflags += ['-DV8_USE_EXTERNAL_STARTUP_DATA=1']
    snapshot_target = 'libv8_external_snapshot.a'
else:
    snapshot_target = 'libv8_nosnapshot.a'


if HAS_ICU4C:
    cflags += ['-DV8_I18N_SUPPORT=1']


extra_objects = []


if not USE_SHARED:
    extra_objects += [os.path.join(STATIC_LIBS_PATH, 'libv8_base.a')]

extra_objects += [
    os.path.join(STATIC_LIBS_PATH, 'libv8_libbase.a'),
    os.path.join(STATIC_LIBS_PATH, snapshot_target),
    os.path.join(STATIC_LIBS_PATH, 'libv8_libplatform.a'),
]

if HAS_ICU4C:
    extra_objects += [
        os.path.join(STATIC_LIBS_PATH, 'libicuuc.a'),
        os.path.join(STATIC_LIBS_PATH, 'libicui18n.a'),
        os.path.join(STATIC_LIBS_PATH, 'libicudata.a'),
    ]

if not IS_MAC:
    extra_objects = ['-Wl,--start-group'] + extra_objects + ['-Wl,--end-group']


ffi.set_source(
    "_v8",
    """
    #include "v8cffi.h"
    """,
    language='c++',
    source_extension='.cpp',
    extra_compile_args=cflags,
    extra_link_args=extra_link_args,
    include_dirs=[
        SRC_PATH,
        os.path.join(SRC_PATH, 'v8')],
    sources=[
        os.path.join(SRC_PATH, 'v8cffi.cpp'),
        os.path.join(SRC_PATH, 'v8cffi_context.cpp'),
        os.path.join(SRC_PATH, 'v8cffi_platform.cpp'),
        os.path.join(SRC_PATH, 'v8cffi_trace_back.cpp'),
        os.path.join(SRC_PATH, 'v8cffi_utils.cpp'),
        os.path.join(SRC_PATH, 'v8cffi_vm.cpp')],
    extra_objects=extra_objects)


ffi.cdef(
    """
    typedef enum
    {
      E_V8_OK = 0,
      E_V8_OUT_OF_MEM_ERROR,
      E_V8_JS_ERROR,
      E_V8_UNKNOWN_ERROR
    } v8_code;

    void v8cffi_free(void *ptr);

    typedef struct v8cffi_platform_s v8cffi_platform_t;

    v8_code v8cffi_platform_new(
      v8cffi_platform_t **platform,
      const char *natives_blob,
      size_t natives_blob_len,
      const char *snapshot_blob,
      size_t snapshot_blob_len);
    void v8cffi_platform_free(v8cffi_platform_t *platform);

    typedef struct v8cffi_vm_s v8cffi_vm_t;

    v8_code v8cffi_vm_new(v8cffi_vm_t **vm);
    void v8cffi_vm_free(v8cffi_vm_t *vm);

    typedef struct v8cffi_context_s v8cffi_context_t;

    v8_code v8cffi_context_new(v8cffi_context_t **ctx, v8cffi_vm_t *vm);
    void v8cffi_context_free(v8cffi_context_t *ctx);

    v8_code v8cffi_run_script(
      v8cffi_context_t *ctx,
      const char *input_script,
      size_t input_script_len,
      const char *identifier,
      size_t identifier_len,
      char **output,
      size_t *output_len,
      char **error,
      size_t *error_len);
    """)


if __name__ == "__main__":
    ffi.compile(verbose=1)
    print('ok')
