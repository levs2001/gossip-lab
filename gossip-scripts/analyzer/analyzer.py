import json
import os
from fnmatch import fnmatch
from enum import Enum
from types import SimpleNamespace as Namespace


# { "type": "PUSH", "tm": 1716659669543, "sender": "http://1.loss-0.gossip-worker:8080", "receiver": "http://9.loss-0.gossip-worker:8080", "message": { "hash": "Warm up 11716659649333http://1.loss-0.gossip-worker:808031379903260", "message": "Warm up 1", "infectionCount": 3 } }
class SimpleToStr:
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()


class ReceivedMsg(SimpleToStr):
    def __init__(self, hash: str, message: str, infection_count: int):
        self.hash = hash
        self.message = message
        self.infection_count = infection_count


class MsgType(Enum):
    PUSH = 'PUSH'
    MSG = 'MSG'


class RowLog(SimpleToStr):
    def __init__(self, type: MsgType, tm: int, sender: str, receiver: str, message: ReceivedMsg):
        self.type = type
        self.tm = tm
        self.sender = sender
        self.receiver = receiver
        self.message = message


def row_log_decode(row):
    return RowLog(MsgType[row.type], row.tm, row.sender, row.receiver,
                  ReceivedMsg(row.message.hash, row.message.message, row.message.infectionCount))


class Parser:
    log_pattern = '*.log'
    params_file = 'test_params.json'

    def __init__(self, cluster_dir: str):
        self.cluster_dir = cluster_dir
        self.all_logs: [RowLog] = []
        self.test_start_tm = 0

    def analyze(self):
        with open(os.path.join(self.cluster_dir, Parser.params_file)) as f:
            test_params = json.load(f)
        self.test_start_tm = test_params['test_start_millis']
        print(f'Test start : {self.test_start_tm}')

    def parse_all_logs(self):
        for path, subdirs, files in os.walk(self.cluster_dir):
            for name in files:
                if fnmatch(name, Parser.log_pattern):
                    log_file = os.path.join(path, name)
                    self.parse_log_file(log_file)

    def parse_log_file(self, log_file):
        with open(log_file) as f:
            for line in f:
                row = json.loads(line, object_hook=lambda d: Namespace(**d))
                row: RowLog = row_log_decode(row)
                self.all_logs.append(row)


if __name__ == '__main__':
    parser = Parser('../cluster/containers_count_10/package_loss_0')
    parser.analyze()
    parser.parse_all_logs()
    print(parser.test_start_tm)

    msgs_test = []
    for log in parser.all_logs:
        if log.type == MsgType.MSG:
            if log.tm > parser.test_start_tm:
                print(log)
                msgs_test.append(log)

    print(len(msgs_test))
        # TODO: all_logs to dataframe and filter it, ...
