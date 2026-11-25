package kr.ac.khu.spacecheck;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Handler;
import android.os.Looper;
import android.util.LruCache;
import android.widget.ImageView;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 이미지 URL 을 백그라운드에서 내려받아 ImageView 에 넣는 간단한 로더 (메모리 캐시 포함).
 * 목록을 빨리 스크롤해도 다른 칸의 이미지가 들어가지 않도록 ImageView 의 tag 로 URL 을 확인한다.
 */
public final class ImageLoader {
    private static final LruCache<String, Bitmap> CACHE = new LruCache<String, Bitmap>(16 * 1024 * 1024) {
        @Override
        protected int sizeOf(String key, Bitmap value) {
            return value.getByteCount();
        }
    };
    private static final ExecutorService POOL = Executors.newFixedThreadPool(3);
    private static final Handler MAIN = new Handler(Looper.getMainLooper());

    private ImageLoader() {
    }

    public static void load(String url, ImageView view) {
        view.setTag(url);
        view.setImageDrawable(null);
        if (url == null) return;
        Bitmap cached = CACHE.get(url);
        if (cached != null) {
            view.setImageBitmap(cached);
            return;
        }
        POOL.execute(() -> {
            Bitmap bmp = download(url);
            if (bmp == null) return;
            CACHE.put(url, bmp);
            MAIN.post(() -> {
                if (url.equals(view.getTag())) view.setImageBitmap(bmp);
            });
        });
    }

    private static Bitmap download(String url) {
        HttpURLConnection conn = null;
        try {
            conn = (HttpURLConnection) new URL(url).openConnection();
            conn.setConnectTimeout(15000);
            conn.setReadTimeout(20000);
            try (InputStream in = conn.getInputStream()) {
                return BitmapFactory.decodeStream(in);
            }
        } catch (Exception e) {
            return null;
        } finally {
            if (conn != null) conn.disconnect();
        }
    }
}
