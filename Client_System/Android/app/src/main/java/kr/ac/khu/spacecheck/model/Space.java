package kr.ac.khu.spacecheck.model;

import com.google.gson.annotations.SerializedName;

/** 서버 Space + 가장 최근 Post 요약(latest). */
public class Space {
    public int id;
    public String name;
    public String building;
    public String floor;
    public int capacity;
    @SerializedName("has_outlet")
    public boolean hasOutlet;
    public Latest latest;          // 아직 Post 가 없으면 null

    public static class Latest {
        @SerializedName("post_id")
        public int postId;
        @SerializedName("person_count")
        public int personCount;
        public String level;
        public String image;
        @SerializedName("published_date")
        public String publishedDate;
    }
}
