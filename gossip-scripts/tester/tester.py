import os
import time
import json
import requests
import logging
import shutil
import subprocess

log = logging.getLogger('Tester')
log.setLevel(logging.INFO)


class Composer:
    def __init__(self, compose_file: str):
        self.compose_file = compose_file

    def compose_up(self):
        subprocess.Popen(f'docker-compose -f {self.compose_file} up', shell=True)

    def compose_down(self):
        subprocess.call(f'docker-compose -f {self.compose_file} down', shell=True)


# Use for absolute time not for delta
def time_millis():
    return time.time_ns() // 1_000_000


class Tester:
    cluster_init_seconds: float = 90
    check_delta_sec: float = 5
    check_attempts: int = 10
    warm_up_delta_sec: float = 1
    tester_delta_sec: float = 2
    request_timeout: float = 1.5

    def __init__(self, cluster_dir: str, msg_receiver_url, inf_count, msg_count, warm_up_count=100,
                 remove_old_logs=True):
        self.volumes_path = cluster_dir + '/volumes'
        self.cluster_dir = cluster_dir
        self.composer = Composer(cluster_dir + '/docker-compose.yml')
        self.msg_receiver_url = msg_receiver_url
        self.inf_count = inf_count
        self.msg_count = msg_count
        self.warm_up_count = warm_up_count
        self.remove_old_logs = remove_old_logs

        self.test_params = {}
        self._write_param('inf_count', inf_count)
        self._write_param('msg_count', msg_count)
        self._write_param('warm_up_count', warm_up_count)

    def make_test(self):
        self._warm_up()
        self._make_test()
        self._save_params()

    def cluster_up(self):
        # Чистим volumes_path, чтобы затереть старые логи
        if os.path.exists(self.volumes_path) and self.remove_old_logs:
            log.info(f'Removing old cluster volumes {self.volumes_path}')
            shutil.rmtree(self.volumes_path, ignore_errors=True)
        # Запускаем кластер
        log.info('Starting cluster...')
        self.composer.compose_up()
        # Даем кластеру время чтобы подняться
        time.sleep(Tester.cluster_init_seconds)

        for i in range(Tester.check_attempts):
            log.info(f'Try to send check msg: {i}')
            try:
                ans = self.send_message(f"Cluster is up check {i}")
            except Exception as err:
                log.info(f'Check attempt {i} failed. {err}')
                log.info(f'Waiting {Tester.check_delta_sec} seconds after failed attempt...')
                time.sleep(Tester.check_delta_sec)
                continue

            log.info(f'Received answer for msg: {i}, {ans}')
            if ans.status_code == 200:
                log.info(f'Cluster raised up on message {i}.')
                return True
        log.error('No answer from cluster')
        return False

    def cluster_down(self):
        self.composer.compose_down()
        log.info("Cluster switched off.")

    def _make_test(self):
        log.info('Starting test. Message count: %d', self.msg_count)
        test_start_millis, test_end_millis = self._send_messages('Test msg', self.msg_count,
                                                                 Tester.tester_delta_sec)
        log.info('Test finished.')

        self._write_param('test_start_millis', test_start_millis)
        self._write_param('test_end_millis', test_end_millis)

    def _warm_up(self):
        if not self.warm_up_count:
            return
        log.info('Starting warmup. Message count: %d', self.warm_up_count)
        warm_up_start_millis, warm_up_end_millis = self._send_messages('Warm up', self.warm_up_count,
                                                                       Tester.warm_up_delta_sec)
        log.info('Warmup finished.')

        self._write_param('warm_up_start_millis', warm_up_start_millis)
        self._write_param('warm_up_end_millis', warm_up_end_millis)

    def _send_messages(self, prefix: str, count: int, delta_sec: float):
        start = time_millis()
        for i in range(count):
            if i % 10 == 0:
                log.info(f'{prefix} {i / count} persents.')
            msg = prefix + f' {i}'
            try:
                self.send_message(msg)
            except Exception as e:
                log.error(f'Exception during message {msg} sending: {e}')
            time.sleep(delta_sec)
        end = time_millis()

        return start, end

    def send_message(self, message: str):
        params = {'infectionCount': self.inf_count, 'message': message}
        return requests.post(url=self.msg_receiver_url, params=params, timeout=Tester.request_timeout)

    def _save_params(self):
        with open(self.cluster_dir + '/test_params.json', 'w') as f:
            json.dump(self.test_params, f)

    def _write_param(self, param_name, param_value):
        self.test_params[param_name] = param_value


if __name__ == '__main__':
    tester = Tester('./cluster/containers_count_10/package_loss_0', 'http://localhost:8000/message/',
                    inf_count=3, msg_count=100)
    tester.make_test()
