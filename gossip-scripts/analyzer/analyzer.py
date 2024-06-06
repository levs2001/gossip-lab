import json
import os
import re
from enum import Enum
from fnmatch import fnmatch
from types import SimpleNamespace as Namespace

import pandas


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

    def __str__(self):
        return f'{self.type.name},{self.tm},{self.sender},{self.receiver},{self.message.hash},{self.message.message},{self.message.infection_count}'

    @staticmethod
    def header():
        return 'type,tm,sender,receiver,hash,message,infection_count'


def row_log_decode(row):
    return RowLog(MsgType[row.type], row.tm, row.sender, row.receiver,
                  ReceivedMsg(row.message.hash, row.message.message, row.message.infectionCount))


class Parser:
    log_pattern = '*.log'
    params_file = 'test_params.json'
    cont_count_prefix = 'containers_count_'

    def __init__(self, cluster_dir: str):
        self.cluster_dir = cluster_dir
        self.all_logs: [RowLog] = []
        self.test_start_tm = 0
        self.msg_count = 0
        self.inf_count = 0
        self.containers_count = 0
        self.package_loss = 0

        self.analyze_meta()

    def get_params(self):
        result_dict = {
            'inf_count': self.inf_count,
            'package_loss_perc': self.package_loss,
            'containers_count': self.containers_count,
            'msg_count': self.msg_count
        }

        df = self.make_df()
        df = df.loc[df['tm'] > self.test_start_tm]

        # Среднее время распространения и время последнего
        messages_tm = df[df['type'] == 'MSG'][['tm', 'hash']]
        push = df.loc[df['type'] == 'PUSH']
        min_push_tm = push.groupby(['hash', 'receiver'], as_index=False).agg({'tm': 'min'})
        with_time = min_push_tm.join(messages_tm.set_index('hash'), lsuffix='_push', rsuffix='_msg', on='hash')
        with_time['send_ms'] = with_time['tm_push'] - with_time['tm_msg']
        with_time_agg = with_time.groupby('hash', as_index=False).agg({'send_ms': ['max', 'mean']})
        result_dict['max_send_ms'] = with_time_agg[('send_ms', 'max')].mean()
        result_dict['mean_send_ms'] = with_time_agg[('send_ms', 'mean')].mean()

        # Процент распространения и дубликатов
        ag = df.groupby('hash').agg({'receiver': ['nunique']})
        unique_msg = ag.sum().iloc[0]
        result_dict['infected_perc'] = unique_msg / (self.msg_count * self.containers_count) * 100

        # Процент сообщений дубликатов
        all_msg = df.groupby(['hash', 'receiver']).count().sum().iloc[0]
        result_dict['duplicate_perc'] = (all_msg - unique_msg) / all_msg * 100

        return result_dict

    def make_df(self):
        self.parse_all_logs()
        filename = f'{self.cluster_dir}/cc_{self.containers_count}_pl_{self.package_loss}_ic_{self.inf_count}.csv'
        with open(filename, 'w') as f:
            f.write(RowLog.header() + '\n')
            for log in self.all_logs:
                f.write(str(log) + '\n')
        return pandas.read_csv(filename)

    def analyze_meta(self):
        self.containers_count = int(re.search(r"containers_count_(.+?)/", self.cluster_dir).group(1))
        self.package_loss = int(re.search(r"package_loss_(.*)", self.cluster_dir).group(1))

        with open(os.path.join(self.cluster_dir, Parser.params_file)) as f:
            test_params = json.load(f)
        self.test_start_tm = test_params['test_start_millis']
        self.inf_count = test_params['inf_count']
        self.msg_count = test_params['msg_count']
        print(f'Test start : {self.test_start_tm}')
        print(f'Message count : {self.msg_count}')
        print(f'Infection count : {self.inf_count}')

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
    print(parser.get_params())
