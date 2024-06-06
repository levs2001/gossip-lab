package leo.worker.network;

import java.util.concurrent.ThreadLocalRandom;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class NetworkTroubleMaker implements INetworkTroublemaker {
    private final int packageLoss;

    public NetworkTroubleMaker(@Value("${network.package.loss}") int packageLoss) {
        this.packageLoss = packageLoss;
    }

    @Override
    public boolean isMessageLost() {
        return ThreadLocalRandom.current().nextInt(100) < packageLoss;
    }
}
