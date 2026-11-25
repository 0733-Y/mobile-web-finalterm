package kr.ac.khu.spacecheck.model;

import com.google.gson.annotations.SerializedName;

/** 서버 Post (Edge 가 올린 스냅샷 한 장). 필드 이름은 Django PostSerializer 와 같다. */
public class Post {
    public int id;
    public Integer space;          // 공간 id (없을 수 있음)
    public String title;
    public String text;
    public String image;           // 이미지 절대 URL (없을 수 있음)
    @SerializedName("person_count")
    public int personCount;
    public String level;           // 여유 / 보통 / 혼잡 (없을 수 있음)
    @SerializedName("published_date")
    public String publishedDate;   // ISO 8601, 예: 2026-11-24T12:48:24.643683+09:00
}
