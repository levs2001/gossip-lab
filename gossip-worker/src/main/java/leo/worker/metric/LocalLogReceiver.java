package leo.worker.metric;

import leo.worker.domain.ReceivedMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class LocalLogReceiver implements ILogReceiver {
    // TODO Настроить этот логгер на запись в файл
    private static final Logger log = LoggerFactory.getLogger(LocalLogReceiver.class);

    @Override
    public boolean logMsg(ReceivedMessage message, String receiver) {
        log.info("Logged message, tm: {}, message: {}", System.currentTimeMillis(), message);
        return true;
    }

    @Override
    public void logPush(ReceivedMessage message, String sender, String receiver) {
        log.info("Logged push, tm: {}, sender: {}, receiver: {}, message: {}", System.currentTimeMillis(), sender, receiver, message);
    }
}
