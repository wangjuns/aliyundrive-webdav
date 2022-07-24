import importlib
import os

pardir = os.path.dirname(os.path.abspath(__file__))


def get_ext_file_checks():
    check_funcs = {}

    for filename in os.listdir(pardir):
        if filename.startswith('_') or not filename.endswith('check.py'):
            continue

        m = importlib.import_module(f'exts.{os.path.splitext(filename)[0]}')
        if hasattr(m, 'encryption_mode') and hasattr(m, 'check'):
            check_funcs[m.encryption_mode] = m.check

    return check_funcs


def get_ext_file_classes():
    file_classes = {}

    for filename in os.listdir(pardir):
        if filename.startswith('_') or not filename.endswith('.py'):
            continue

        m = importlib.import_module(f'exts.{os.path.splitext(filename)[0]}')
        if hasattr(m, 'encryption_mode') and hasattr(m, 'file_class'):
            file_classes[m.encryption_mode] = m.file_class

    return file_classes
