package leo.worker.client;

import leo.worker.IGossipWorkerService;
import leo.worker.domain.ReceivedMessage;
import org.springframework.http.ResponseEntity;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.support.WebClientAdapter;
import org.springframework.web.service.invoker.HttpServiceProxyFactory;

public class GossipWorkerClient implements IGossipWorkerService {
    private final IGossipWorkerService client;

    public GossipWorkerClient(String host) {
        WebClient webClient = WebClient.builder()
            .baseUrl(host)
            .build();
        HttpServiceProxyFactory httpServiceProxyFactory = HttpServiceProxyFactory
            .builder(WebClientAdapter.forClient(webClient))
            .build();

        this.client = httpServiceProxyFactory.createClient(IGossipWorkerService.class);
    }

    @Override
    public ResponseEntity<String> message(String message, int infectionCount) {
        return client.message(message, infectionCount);
    }

    @Override
    public ResponseEntity<String> push(ReceivedMessage msg, String sender) {
        return client.push(msg, sender);
    }
}
