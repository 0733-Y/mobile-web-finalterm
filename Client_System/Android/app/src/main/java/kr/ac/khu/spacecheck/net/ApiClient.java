package kr.ac.khu.spacecheck.net;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * 서버 주소와 토큰으로 Retrofit 클라이언트를 만든다.
 * 토큰이 있으면 모든 요청에 `Authorization: Token <token>` 헤더를 붙인다 (서버의 DRF TokenAuthentication 과 맞춤).
 */
public final class ApiClient {
    private ApiClient() {
    }

    public static SpaceCheckApi create(String baseUrl, String token) {
        OkHttpClient http = new OkHttpClient.Builder()
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(20, TimeUnit.SECONDS)
                .addInterceptor(chain -> {
                    Request req = chain.request();
                    if (token != null) {
                        req = req.newBuilder().header("Authorization", "Token " + token).build();
                    }
                    return chain.proceed(req);
                })
                .build();
        return new Retrofit.Builder()
                .baseUrl(baseUrl)
                .client(http)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(SpaceCheckApi.class);
    }
}
