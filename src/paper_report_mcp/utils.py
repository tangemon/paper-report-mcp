import sys
import os
import traceback


root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def get_exception_error():
    # Get current system exception
    ex_type, ex_value, ex_traceback = sys.exc_info()

    # Extract stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)

    # Format stacktrace
    stack_trace = list()

    for trace in trace_back:
        stack_trace.append(f"File: {trace[0]}, Line: {trace[1]}, Function: {trace[2]}, Message: {trace[3]}")

    error_msg = f"Exception type: {ex_type.__name__}\n"
    error_msg += f"Exception message: {ex_value}\n"
    error_msg += f"Stack trace: {stack_trace}"
    return error_msg
