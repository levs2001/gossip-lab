package leo.worker.domain;

public record ReceivedMessage(String hash, String message, int infectionCount) {
    public static ReceivedMessage of(String hash, String message, int infectionCount) {
        return new ReceivedMessage(hash, message, infectionCount);
    }

    @Override
    public String toString() {
        return String.format("{ \"hash\": \"%s\", \"message\": \"%s\", \"infectionCount\": %d }", hash, message, infectionCount);
    }
}
