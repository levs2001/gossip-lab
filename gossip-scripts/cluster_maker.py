import os


class ClusterMaker:
    # TODO: Реализовать package_loss
    # TODO: add network in yml
    def __init__(self, image='leo-gossip-worker:0.0.1', internal_port=8080, package_loss=0, containers_count=100,
                 first_port=8000, cluster_path='./cluster'):
        self.image = image
        self.internal_port = internal_port
        self.package_loss = package_loss
        self.containers_count = containers_count
        self.first_port = first_port
        self.cluster_path = cluster_path

    def save_compose(self):
        filename = (f"{self.cluster_path}/containers_count_{self.containers_count}/package_loss_{self.package_loss}"
                    f"/docker-compose.yml")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        hosts = [ClusterMaker._host(port) for port in self._port_range()]
        with open(filename, 'w') as f:
            f.write(self._header_yml())

            for port in self._port_range():
                f.write(self._service_yml(port, hosts))

    def _header_yml(self):
        return f"""# Gossip Cluster, containers_count: {self.containers_count}, package_loss: {self.package_loss} 
version: '3.8'
services:
        """

    def _port_range(self):
        return range(self.first_port, self.first_port + self.containers_count)

    def _service_yml(self, port: int, hosts: [str]):
        service = f"{port}.loss-{self.package_loss}.gossip-worker"
        hosts_str = f"{hosts}"[1:-1].replace("\'", "")
        return f"""
  {service}:
    image: {self.image}
    container_name: {service}
    ports:
      - "{port}:{self.internal_port}"
    volumes:
      - {self.cluster_path}/data/package-loss-{self.package_loss}/host-{port}:/data,size=10Gi
    environment:
      - CLUSTER_OWN_HOST={ClusterMaker._host(port)}
      - CLUSTER_HOSTS={hosts_str}
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.1'
        reservations:
          memory: 100M
          cpus: '0.25'
  """

    @staticmethod
    def _host(port):
        return f"http://localhost:{port}"


if __name__ == '__main__':
    maker = ClusterMaker(containers_count=10)
    maker.save_compose()
