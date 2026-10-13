"""Offline subprocess timing with optional Windows working-set evidence."""
import ctypes
import os
import subprocess
import time


def peak_memory(process=None):
    if os.name != "nt":
        return None
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    data = Counters()
    data.cb = ctypes.sizeof(data)
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    get_info.restype = wintypes.BOOL
    handle = int(process._handle) if process is not None else -1
    if get_info(wintypes.HANDLE(handle), ctypes.byref(data), data.cb):
        return int(data.PeakWorkingSetSize)
    return None


def execute(command):
    started = time.perf_counter()
    maximum = None
    process = subprocess.Popen(command)
    while True:
        current = peak_memory(process)
        if current is not None:
            maximum = current if maximum is None else max(maximum, current)
        result = process.poll()
        if result is not None:
            break
        time.sleep(0.05)
    parent = peak_memory()
    return {"exit_code": result, "seconds": round(time.perf_counter() - started, 3),
            "peak_resident_bytes": maximum, "parent_peak_resident_bytes": parent,
            "combined_peak_upper_bound_bytes": maximum + parent if maximum is not None and parent is not None else None}
