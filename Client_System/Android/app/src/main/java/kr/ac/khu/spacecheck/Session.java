package kr.ac.khu.spacecheck;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * 로그인 결과(토큰)와 선택한 서버 주소를 SharedPreferences 에 저장한다.
 * 비밀번호는 저장하지 않는다. 토큰은 로그인할 때 서버에서 받아오며 코드에 들어 있지 않다.
 */
public final class Session {
    private static final String PREFS = "spacecheck_session";
    private static final String KEY_TOKEN = "token";
    private static final String KEY_SERVER = "server";
    private static final String KEY_USER = "username";

    private final SharedPreferences prefs;

    public Session(Context context) {
        prefs = context.getApplicationContext().getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public String getToken() {
        return prefs.getString(KEY_TOKEN, null);
    }

    public String getServer() {
        return prefs.getString(KEY_SERVER, ServerConfig.ONLINE);
    }

    public String getUsername() {
        return prefs.getString(KEY_USER, "");
    }

    public boolean isLoggedIn() {
        return getToken() != null;
    }

    public void saveLogin(String server, String username, String token) {
        prefs.edit().putString(KEY_SERVER, server).putString(KEY_USER, username)
                .putString(KEY_TOKEN, token).apply();
    }

    public void saveServer(String server) {
        prefs.edit().putString(KEY_SERVER, server).apply();
    }

    /** 로그아웃 또는 토큰 만료(401) 시 토큰만 지운다. 서버 선택·아이디는 남겨 둔다. */
    public void clearToken() {
        prefs.edit().remove(KEY_TOKEN).apply();
    }
}
