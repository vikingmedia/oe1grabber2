import sys

def progressBarCallback(size_total, size):

    progress = (float(size) / size_total) * 100
    progressed = int(progress / 2.5)
    fill = progressed * '='
    blank = (40 - progressed) * '.'
    progressbar = '[%(fill)s>%(blank)s] %(progress)s%%' % {'fill': fill, 'blank': blank, 'progress': int(progress)}

    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        sys.stdout.write('\r')
    else:
        sys.stdout.write('\n')

    sys.stdout.write(progressbar)
    sys.stdout.flush()