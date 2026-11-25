package kr.ac.khu.spacecheck;

import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

/** 서버 시각(ISO 8601) 파싱과 화면 표시 형식. */
public final class TimeUtil {
    private static final DateTimeFormatter SHOW =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm").withZone(ZoneId.of("Asia/Seoul"));

    private TimeUtil() {
    }

    /** 파싱 실패 또는 null 이면 null. */
    public static OffsetDateTime parse(String iso) {
        if (iso == null) return null;
        try {
            return OffsetDateTime.parse(iso);
        } catch (DateTimeParseException e) {
            return null;
        }
    }

    public static String format(OffsetDateTime t) {
        return t == null ? "-" : SHOW.format(t);
    }
}
