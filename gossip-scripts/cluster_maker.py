import os


class ClusterMaker:
    # TODO: Реализовать package_loss
    # TODO: add network in yml
    def __init__(self, open_ports: dict[int, int], image='leo-gossip-worker:0.0.1', internal_port=8080, package_loss=0,
                 containers_count=100, config_path='./cluster',
                 volumes_path='./volumes', limit_mem='256M', reserve_mem='128M'):
        self.image = image
        self.internal_port = internal_port
        self.package_loss = package_loss
        self.containers_count = containers_count
        self.config_path = config_path
        self.volumes_path = volumes_path
        self.network_name = 'gossip-network'
        self.limit_mem = limit_mem
        self.reserve_mem = reserve_mem
        self.open_ports = open_ports

    def save_compose(self):
        filename = (f"{self.config_path}/containers_count_{self.containers_count}/package_loss_{self.package_loss}"
                    f"/docker-compose.yml")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        hosts = [self._host(port) for port in self._num_range()]
        with open(filename, 'w') as f:
            f.write(self._header_yml())

            for num in self._num_range():
                open_port = self.open_ports[num] if num in self.open_ports else None
                f.write(self._service_yml(num, hosts, open_port))

            f.write(self._footer_yml())

    def _header_yml(self):
        return f"""# Gossip Cluster, containers_count: {self.containers_count}, package_loss: {self.package_loss} 
version: '3.8'
services:
        """

    def _footer_yml(self):
        return f"""
networks:
  {self.network_name}:
    driver: bridge
        """

    def _num_range(self):
        return range(1, self.containers_count + 1)

    def _service_yml(self, num: int, hosts: [str], open_port=None):
        service = self._service(num)
        hosts_str = f"{hosts}"[1:-1].replace("\'", "")
        ports = f"""
    ports:
      - "{open_port}:{self.internal_port}" """ if open_port else ''

        return f"""
  {service}:
    image: {self.image}
    container_name: {service}{ports}
    volumes:
      - {self.volumes_path}/host-{num}:/opt/app/data
    environment:
      - CLUSTER_OWN_HOST={self._host(num)}
      - CLUSTER_HOSTS={hosts_str}
    deploy:
      resources:
        limits:
          memory: {self.limit_mem}
          cpus: '0.1'
        reservations:
          memory: {self.reserve_mem}
          cpus: '0.25'
    networks:
      - {self.network_name}
  """

    def _service(self, num):
        return f"{num}.loss-{self.package_loss}.gossip-worker"

    def _host(self, num):
        # Port is fixed for all, host is different
        return f"http://{self._service(num)}:{self.internal_port}"


if __name__ == '__main__':
    maker = ClusterMaker(containers_count=10, open_ports={1: 8000, 2: 8001})
    maker.save_compose()
