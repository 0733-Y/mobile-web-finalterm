package kr.ac.khu.spacecheck;

import android.view.View;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

/**
 * Android 15 이상은 화면이 상태바·내비게이션바 아래까지 그려진다(edge-to-edge).
 * 루트 뷰에 시스템 바 크기만큼 여백을 주고, 레이아웃 안의 Toolbar 를 액션바로 쓴다.
 */
public final class SystemBars {
    private SystemBars() {
    }

    public static void setup(AppCompatActivity activity, int rootId, int toolbarId) {
        Toolbar toolbar = activity.findViewById(toolbarId);
        activity.setSupportActionBar(toolbar);
        View root = activity.findViewById(rootId);
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, windowInsets) -> {
            Insets bars = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars() | WindowInsetsCompat.Type.ime());
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            return WindowInsetsCompat.CONSUMED;
        });
    }
}
