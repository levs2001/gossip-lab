package leo.worker;

import java.util.concurrent.ThreadLocalRandom;
import leo.worker.client.IGossipWorkerClient;
import leo.worker.cluster.IClusterInfo;
import leo.worker.cluster.IGossipCluster;
import leo.worker.domain.ReceivedMessage;
import leo.worker.metric.ILogReceiver;
import leo.worker.network.INetworkTroublemaker;
import leo.worker.util.FixedSizeSet;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GossipWorkerController {
    public static final String MESSAGE_M = "message/";
    public static final String PUSH_M = "push/";
    private static final Logger log = LoggerFactory.getLogger(GossipWorkerController.class);
    private final FixedSizeSet<String> lastHashes = new FixedSizeSet<>(400);
    private final ILogReceiver logReceiver;
    private final IGossipCluster cluster;
    private final INetworkTroublemaker networkTroublemaker;
    private final String ownHost;

    public GossipWorkerController(
        ILogReceiver logReceiver, IGossipCluster cluster, IClusterInfo clusterInfo, INetworkTroublemaker networkTroublemaker) {
        this.logReceiver = logReceiver;
        this.cluster = cluster;
        this.ownHost = clusterInfo.getOwnHost();
        this.networkTroublemaker = networkTroublemaker;
    }

    @PostMapping(MESSAGE_M)
    public ResponseEntity<String> message(@RequestParam String message, @RequestParam int infectionCount) {
        log.info("Received message: {}, infectionCount: {}", message, infectionCount);
        String hash = getHash(message, infectionCount, ownHost);
        ReceivedMessage receivedMessage = ReceivedMessage.of(hash, message, infectionCount);
        if (logReceiver.logMsg(receivedMessage, ownHost)) {
            lastHashes.add(hash);
            cluster.pushGossip(receivedMessage);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.internalServerError().build();
    }

    @PostMapping(PUSH_M)
    public ResponseEntity<String> push(@RequestBody ReceivedMessage message, @RequestParam String sender) {
        if (networkTroublemaker.isMessageLost()) {
            log.info("Lost Push: {}, sender: {}, due to special network problems.", message, sender);
            return ResponseEntity.ok().build();
        }

        log.info("Received push: {}, sender: {}", message, sender);

        logReceiver.logPush(message, sender, ownHost);
        if (lastHashes.add(message.hash())) {
            cluster.pushGossip(message);
            log.info("Message: {} pushed further in cluster", message);
        } else {
            log.info("Message: {} already pushed.", message);
        }

        return ResponseEntity.ok().build();
    }

    private static String getHash(String message, int infectionCount, String ownNode) {
        return message + System.currentTimeMillis() + ownNode + infectionCount + ThreadLocalRandom.current().nextInt();
    }
}
