package kr.ac.khu.spacecheck;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.time.OffsetDateTime;

import org.junit.Test;

/** 데이터 오래됨 판정: 정상(10분 이내) / 규칙 위반(10분 초과) / 정보 부족(시각 없음). */
public class StaleCheckerTest {
    private static final OffsetDateTime NOW = OffsetDateTime.parse("2026-11-25T15:00:00+09:00");

    @Test
    public void freshWithinTenMinutes() {
        assertFalse(StaleChecker.isStale(NOW.minusMinutes(9), NOW));
        assertFalse(StaleChecker.isStale(NOW.minusMinutes(10), NOW));   // 정확히 10분은 아직 오래되지 않음
    }

    @Test
    public void staleAfterTenMinutes() {
        assertTrue(StaleChecker.isStale(NOW.minusMinutes(10).minusSeconds(1), NOW));
        assertTrue(StaleChecker.isStale(NOW.minusHours(3), NOW));
    }

    @Test
    public void missingTimeIsStale() {
        assertTrue(StaleChecker.isStale(null, NOW));
    }

    @Test
    public void parsesServerTimeWithOffset() {
        OffsetDateTime t = TimeUtil.parse("2026-11-24T12:48:24.643683+09:00");
        assertFalse(StaleChecker.isStale(t, t.plusMinutes(5)));
        assertTrue(StaleChecker.isStale(t, t.plusMinutes(11)));
    }
}
