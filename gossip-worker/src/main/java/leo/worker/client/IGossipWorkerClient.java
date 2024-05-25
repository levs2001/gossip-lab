package leo.worker.client;

import leo.worker.domain.ReceivedMessage;
import reactor.core.publisher.Mono;

public interface IGossipWorkerClient {
    Mono<String> push(ReceivedMessage msg, String sender);
}
