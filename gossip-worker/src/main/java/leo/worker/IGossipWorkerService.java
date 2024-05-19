package leo.worker;

import io.swagger.v3.oas.annotations.Operation;
import leo.worker.domain.ReceivedMessage;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.service.annotation.HttpExchange;
import org.springframework.web.service.annotation.PostExchange;

@HttpExchange("/gossip")
public interface IGossipWorkerService {
    String MESSAGE_M = "message/";
    String PUSH_M = "push/";

    @Operation(summary = "Message from real client to our cluster")
    @PostExchange(MESSAGE_M)
    ResponseEntity<String> message(@RequestParam String message, @RequestParam int infectionCount);

    @Operation(summary = "Internal method for gossip communication")
    @PostExchange(PUSH_M)
    ResponseEntity<String> push(@RequestBody ReceivedMessage msg, @RequestParam String sender);
}
