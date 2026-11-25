package kr.ac.khu.spacecheck;

import android.graphics.Color;

/** 혼잡도 등급 표시 색: 여유=초록, 보통=노랑, 혼잡=빨강, 그 외=회색. */
public final class LevelStyle {
    private LevelStyle() {
    }

    public static int color(String level) {
        if ("여유".equals(level)) return Color.parseColor("#2E9E4F");
        if ("보통".equals(level)) return Color.parseColor("#D9A400");
        if ("혼잡".equals(level)) return Color.parseColor("#D33A2C");
        return Color.parseColor("#888888");
    }

    public static String label(String level) {
        return (level == null || level.isEmpty()) ? "등급 없음" : level;
    }
}
