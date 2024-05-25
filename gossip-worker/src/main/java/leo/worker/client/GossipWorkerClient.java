package leo.worker.client;

import static leo.worker.GossipWorkerController.PUSH_M;

import leo.worker.domain.ReceivedMessage;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

public class GossipWorkerClient implements IGossipWorkerClient {
    private static final String SENDER_P = "sender";

    private final WebClient client;

    public GossipWorkerClient(String host) {
        this.client = WebClient.builder()
            .baseUrl(host)
            .build();
    }

    @Override
    public Mono<String> push(ReceivedMessage msg, String sender) {
        return client.post()
            .uri(
                uriBuilder -> uriBuilder
                    .path(PUSH_M)
                    .queryParam(SENDER_P, sender)
                    .build()
            )
            .bodyValue(msg)
            .accept(MediaType.ALL)
            .retrieve()
            .bodyToMono(String.class);
    }
}
