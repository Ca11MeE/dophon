import platform


def is_windows():
    return 'Windows' == platform.system()


def is_not_windows():
    return not is_windows()
