import os


def load_list(filename):
    values = []
    if not os.path.isfile(filename):
        return values
    else:
        for line in open(filename):
            values.append(line.rstrip())
        return values


def save_list(values, filename):
    with open(filename, 'w') as fd:
        for v in values:
            fd.write(str(v) + '\n')


def load_tuples_list(filename, sep=' '):
    values = []
    if not os.path.isfile(filename):
        return values
    else:
        for line in open(filename):
            values.append(tuple(line.rstrip().split(sep)))
        return values


def save_tuples_list(values, filename, sep=' '):
    with open(filename, 'w') as fd:
        for v1, v2 in values:
            fd.write(str(v1) + sep + str(v2) + '\n')
