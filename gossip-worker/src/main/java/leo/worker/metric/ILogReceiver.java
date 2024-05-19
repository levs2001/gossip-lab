package leo.worker.metric;

import leo.worker.domain.ReceivedMessage;

public interface ILogReceiver {
    /**
     * @param receiver - node that get this message
     * @return true if message was logged, false otherwise
     */
    boolean logMsg(ReceivedMessage message, String receiver);

    /**
     * @param sender - from which node was sent this message (last in chain, not original)
     * @param receiver - node that get this message
     */
    void logPush(ReceivedMessage message, String sender, String receiver);
}
