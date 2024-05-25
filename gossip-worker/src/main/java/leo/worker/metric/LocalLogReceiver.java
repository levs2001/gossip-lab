package leo.worker.metric;

import leo.worker.domain.ReceivedMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class LocalLogReceiver implements ILogReceiver {
    private static final Logger log = LoggerFactory.getLogger(LocalLogReceiver.class);
    private static final String CLIENT_SENDER = "client";

    @Override
    public boolean logMsg(ReceivedMessage message, String receiver) {
        logJson(MsgType.MSG, CLIENT_SENDER, receiver, message);
        return true;
    }

    @Override
    public void logPush(ReceivedMessage message, String sender, String receiver) {
        logJson(MsgType.PUSH, sender, receiver, message);
    }

    private void logJson(MsgType msgType, String sender, String receiver, ReceivedMessage message) {
        log.info("{ \"type\": \"{}\", \"tm\": {}, \"sender\": \"{}\", \"receiver\": \"{}\", \"message\": {} }",
            msgType, System.currentTimeMillis(), sender, receiver, message);
    }

    private enum MsgType {
        MSG,
        PUSH
    }
}
