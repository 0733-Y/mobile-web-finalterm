package kr.ac.khu.spacecheck.net;

import kr.ac.khu.spacecheck.model.Page;
import kr.ac.khu.spacecheck.model.Post;
import kr.ac.khu.spacecheck.model.Space;
import kr.ac.khu.spacecheck.model.TokenResponse;
import retrofit2.Call;
import retrofit2.http.Field;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Path;
import retrofit2.http.Query;
import retrofit2.http.Url;

/** Django REST API 정의 (Retrofit). App 은 토큰 발급 외에는 조회(GET)만 한다. */
public interface SpaceCheckApi {

    /** 아이디·비밀번호로 토큰 발급 (DRF obtain_auth_token). */
    @FormUrlEncoded
    @POST("api-token-auth/")
    Call<TokenResponse> login(@Field("username") String username, @Field("password") String password);

    /** Post 목록 (서버에서 최신순). space 가 null 이면 전체. 2-4 / 3-2 */
    @GET("api_root/Post/")
    Call<Page<Post>> posts(@Query("space") Integer spaceId);

    /** 다음 페이지 (DRF 가 돌려준 next URL 그대로 사용). */
    @GET
    Call<Page<Post>> postsPage(@Url String nextUrl);

    /** Post 상세. 2-4 / 3-2 */
    @GET("api_root/Post/{id}/")
    Call<Post> post(@Path("id") int id);

    /** 공간 목록 + 공간별 최신 상태 (필터 선택지와 데이터 갱신 시각에 사용). */
    @GET("api_root/Space/")
    Call<Page<Space>> spaces();
}
