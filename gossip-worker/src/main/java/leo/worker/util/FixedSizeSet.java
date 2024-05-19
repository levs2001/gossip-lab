package leo.worker.util;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * If size() > maxSize the oldest element will be deleted.
 * Thread safe, blocking
 */
public class FixedSizeSet<K> {
    private static final Object stub = new Object();
    private final Map<K, Object> delegate;

    public FixedSizeSet(int maxSize) {
        delegate = Collections.synchronizedMap(new LinkedHashMap<>() {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K, Object> eldest) {
                return size() > maxSize;
            }
        });
    }

    public boolean add(K k) {
        if (contains(k)) {
            return false;
        } else {
            delegate.put(k, stub);
            return true;
        }
    }

    public boolean contains(K k) {
        return delegate.containsKey(k);
    }

    public boolean notContains(K k) {
        return !contains(k);
    }
}
