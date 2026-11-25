package kr.ac.khu.spacecheck;

import java.time.Duration;
import java.time.OffsetDateTime;

/**
 * 데이터 오래됨 판정. 마지막 갱신 시각에서 STALE_MINUTES 분(600초)을 초과해 지났으면 오래된 데이터로 본다.
 * N=10 은 학생이 정한 값 (2026-11-25). Edge 의 최소 업로드 간격(10초)보다 충분히 길다.
 */
public final class StaleChecker {
    public static final int STALE_MINUTES = 10;

    private StaleChecker() {
    }

    /** lastUpdate 가 null(아직 데이터 없음)이면 오래됨으로 본다. */
    public static boolean isStale(OffsetDateTime lastUpdate, OffsetDateTime now) {
        if (lastUpdate == null) return true;
        return Duration.between(lastUpdate, now).getSeconds() > STALE_MINUTES * 60L;
    }
}
