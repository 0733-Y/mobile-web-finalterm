package kr.ac.khu.spacecheck;

/**
 * 접속할 서버 주소 목록. 로그인 화면에서 고르고, 선택값은 {@link Session} 에 저장된다.
 * - LOCAL : 에뮬레이터에서 PC 의 Django(runserver)에 접속 (10.0.2.2 = PC 의 127.0.0.1)
 * - ONLINE: PythonAnywhere 배포 서버
 */
public final class ServerConfig {
    public static final String LOCAL = "http://10.0.2.2:8000/";
    public static final String ONLINE = "https://0733.pythonanywhere.com/";

    /** 로그인 화면의 선택지 (표시 이름, 주소) — 순서가 Spinner 순서. */
    public static final String[] LABELS = {"온라인 (0733.pythonanywhere.com)", "에뮬레이터 로컬 (10.0.2.2:8000)"};
    public static final String[] URLS = {ONLINE, LOCAL};

    private ServerConfig() {
    }

    public static int indexOf(String url) {
        for (int i = 0; i < URLS.length; i++) {
            if (URLS[i].equals(url)) return i;
        }
        return 0;
    }
}
