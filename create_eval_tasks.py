#!/usr/bin/env python3

import itertools

def filename(comb_list):
    return '_'.join(map(str, comb_list)) + '_all.mat'

if __name__ == '__main__':

    nb_img = 10
    root_dir = "/work/mpizenbe/client/icugleo/src"
    root_results = "/work/mpizenbe/icugleo_results"
    dataset = "axel"
    scribbles_set = ["100", "101", "102", "103", "104", "106",
            "200", "201", "202", "203", "204", "205", "206", "207"]

    with open("tasks_list.sh", 'w') as f:
        for scribble_set in scribbles_set:
            command = './run_evals.sh "../datasets/{0}" "{{{1}}}" && cd .. && tar -cf datasets/{0}/results/eval/{1}.tar'.format(dataset, scribble_set)
            result_file = '$(pwd)/datasets/{0}/results/eval/{1}.tar'.format(dataset, scribble_set)
            line = 'cd ' + root_dir + ' && ' + command + ' && echo ' + result_file
            f.write(line + '\n')

    with open("results_paths.txt", 'w') as f:
        for scribble_set in scribbles_set:
            results_file = '{0}/{1}/eval/{2}.tar'.format(root_results, dataset, scribble_set)
            f.write(results_file + '\n')
