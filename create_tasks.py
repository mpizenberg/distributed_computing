#!/usr/bin/env python3

import itertools

def filename(comb_list):
    return '_'.join(map(str, comb_list)) + '_all.mat'

if __name__ == '__main__':
    
    nb_img = 10
    all_combs = [];
    root_dir = "/work/mpizenbe/client/icugleo/src"
    root_results = "/work/mpizenbe/icugleo_results"
    dataset = "axel"
    scribbles_set = ["100", "101", "102", "103", "104", "106",
            "200", "201", "202", "203", "204", "205", "206", "207"]
    
    
    for i in range(1,nb_img+1):
        all_combs.append(itertools.combinations(range(1,nb_img+1), i))
    all_combs = list(itertools.chain.from_iterable(all_combs))
    
    with open("tasks_list.sh", 'w') as f:
        for scribble_set in scribbles_set:
            for comb in all_combs:
                comb = list(comb)
                command = './run.sh "../datasets/{}" "{}" "{}" "true" && cd ..'.format(dataset, scribble_set, comb)
                result_file = '$(pwd)/datasets/{}/results/coseg/{}/{}'.format(dataset, scribble_set, filename(comb))
                line = 'cd ' + root_dir + ' && ' + command + ' && echo ' + result_file
                f.write(line + '\n')
    
    with open("results_paths.txt", 'w') as f:
        for scribble_set in scribbles_set:
            for comb in all_combs:
                comb = list(comb)
                results_file = '{}/{}/coseg/{}/{}'.format(root_results, dataset, scribble_set, filename(comb))
                f.write(results_file + '\n')
