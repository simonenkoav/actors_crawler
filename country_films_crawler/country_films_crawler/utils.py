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
