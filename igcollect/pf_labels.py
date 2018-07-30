#!/usr/bin/env python
"""igcollect - FreeBSD Packet Filter

Copyright (c) 2018 InnoGames GmbH
"""

from __future__ import print_function
from argparse import ArgumentParser
from socket import gethostname
from subprocess import check_output
import re
import time


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--prefix', default='network')
    return parser.parse_args()


def parse_pf_labels():
    # Get pfctl result of "show all labels"
    pfctl_result = check_output(['/sbin/pfctl', '-q', '-sl'])

    label_counters = {}

    # Read all lines
    for line in pfctl_result.splitlines():

        # Split each line by  ' ', this gives is the label name and values
        line_tab = line.split(' ')

        # Cut unnecessary things out of label
        label = line_tab[0].split(':')[0]
        label = re.sub('_pub$', '', label)
        label = re.sub('_loc$', '', label)

        if label not in label_counters:
            label_counters[label] = {}
            label_counters[label]['p_in'] = int(line_tab[4])
            label_counters[label]['b_in'] = int(line_tab[5])
            label_counters[label]['p_out'] = int(line_tab[6])
            label_counters[label]['b_out'] = int(line_tab[7])
        else:
            label_counters[label]['p_in'] += int(line_tab[4])
            label_counters[label]['b_in'] += int(line_tab[5])
            label_counters[label]['p_out'] += int(line_tab[6])
            label_counters[label]['b_out'] += int(line_tab[7])
    return label_counters


def main():
    args = parse_args()
    hostname = gethostname().replace('.', '_')
    now = str(int(time.time()))
    label_counters = parse_pf_labels()
    for label in label_counters:
        for key in (
            ('bytesIn', 'b_in'),
            ('bytesOut', 'b_out'),
            ('pktsIn', 'p_out'),
            ('pktsOut', 'p_out'),
        ):
            print('{}.{}.{}.{} {} {}'.format(
                args.prefix,
                label, hostname, key[0],
                label_counters[label][key[1]],
                now,
            ))


if __name__ == '__main__':
    main()