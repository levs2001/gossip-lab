import json
import logging
import os.path
import time

from analyzer.analyzer import Parser
from cluster_maker import ClusterMaker
from tester.tester import Tester

msg_count = 100
warm_up_count = 100
open_ports = {1: 8000, 2: 8001}
msg_receiver = 'http://localhost:8000/message/'


def full_trial(containers_count: int, package_loss: int, inf_count_list: [int], make_new: bool):
    maker = ClusterMaker(containers_count=containers_count, package_loss=package_loss, open_ports=open_ports,
                         limit_mem='128M', reserve_mem='100M')
    cluster_dir = maker.get_cluster_dir()

    result_filename = cluster_dir + '/trial_result.json'
    if not make_new and os.path.exists(result_filename):
        print(f'Trial {cluster_dir} skipped.')
        return json.load(open(result_filename, 'r'))

    maker.save_compose()

    trial_results = []

    for i in range(len(inf_count_list)):
        tester = Tester(cluster_dir=cluster_dir, msg_receiver_url=msg_receiver,
                        inf_count=inf_count_list[i], msg_count=msg_count, warm_up_count=warm_up_count)
        if i == 0:  # Костыль, чтобы поднимать кластер при первом запуске
            if not tester.cluster_up():
                tester.cluster_up()
                logging.error('Cant raise cluster.')
                return
        tester.make_test()
        parser = Parser(cluster_dir)
        res = parser.get_params()
        trial_results.append(res)
        print(f'Finished inf_count: {i} for {cluster_dir}')
        print(res)
        if i == len(inf_count_list) - 1:  # Костыль, чтобы гасить кластер в конце
            tester.cluster_down()
        time.sleep(5)

    with open(result_filename, 'w') as f:
        json.dump(trial_results, f)
    return trial_results


if __name__ == '__main__':
    containers_count = 50
    inf_count_l = [inf_count for inf_count in range(3, 10, 2)]
    rows = []
    for package_loss in range(0, 100, 10):
        trial = full_trial(containers_count=containers_count, package_loss=package_loss, inf_count_list=inf_count_l,
                           make_new=False)
        rows.extend(trial)
    with open(f'./trial_result/cc_{containers_count}.json', 'w') as f:
        json.dump(rows, f)
