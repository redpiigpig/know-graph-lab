import sys, os, ctypes, traceback

sys.stdout = sys.stderr  # stderr 也走 stdout，確保 Claude 看得到

_CUDA = r'C:\Users\user\AppData\Local\Programs\Ollama\lib\ollama\cuda_v12'
if os.path.exists(_CUDA):
    os.add_dll_directory(_CUDA)
    for dll in ['cudart64_12.dll', 'cublas64_12.dll', 'cublasLt64_12.dll']:
        try:
            ctypes.CDLL(os.path.join(_CUDA, dll))
            print('DLL OK:', dll)
        except OSError as e:
            print('DLL FAIL:', dll, e)

print('載入 faster_whisper...')
try:
    from faster_whisper import WhisperModel
    print('faster_whisper import OK')
    print('載入 large-v3 model (float16, cuda)...')
    model = WhisperModel('large-v3', device='cuda', compute_type='float16')
    print('large-v3 載入成功！')
except Exception as e:
    print('ERROR:', e)
    traceback.print_exc()
    print('\n--- 改試 int8_float16 ---')
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel('large-v3', device='cuda', compute_type='int8_float16')
        print('int8_float16 載入成功！')
    except Exception as e2:
        print('ERROR:', e2)
        traceback.print_exc()
