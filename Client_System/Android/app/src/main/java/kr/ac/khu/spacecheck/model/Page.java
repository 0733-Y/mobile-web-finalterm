package kr.ac.khu.spacecheck.model;

import java.util.List;

/** DRF 페이지네이션 응답 {count, next, previous, results}. */
public class Page<T> {
    public int count;
    public String next;
    public String previous;
    public List<T> results;
}
