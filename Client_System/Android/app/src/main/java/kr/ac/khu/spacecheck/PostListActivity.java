package kr.ac.khu.spacecheck;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import kr.ac.khu.spacecheck.model.Page;
import kr.ac.khu.spacecheck.model.Post;
import kr.ac.khu.spacecheck.model.Space;
import kr.ac.khu.spacecheck.net.ApiClient;
import kr.ac.khu.spacecheck.net.SpaceCheckApi;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Post 목록 화면 (3-1, 3-2). 최신순, 아래로 당겨 새로고침, 끝까지 스크롤하면 다음 페이지.
 * 상단 Spinner 로 공간별 필터(?space=id), 그 아래에 데이터 오래됨 안내.
 */
public class PostListActivity extends AppCompatActivity {

    private Session session;
    private SpaceCheckApi api;
    private PostAdapter adapter;
    private SwipeRefreshLayout refresh;
    private Spinner spaceSpinner;
    private TextView staleBanner;
    private TextView emptyText;

    private final List<Space> spaces = new ArrayList<>();
    private Integer selectedSpaceId = null;   // null = 전체
    private String nextUrl = null;            // 다음 페이지 URL (없으면 null)
    private boolean loading = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_post_list);
        SystemBars.setup(this, R.id.root, R.id.toolbar);
        session = new Session(this);
        api = ApiClient.create(session.getServer(), session.getToken());

        refresh = findViewById(R.id.refresh);
        spaceSpinner = findViewById(R.id.space_spinner);
        staleBanner = findViewById(R.id.stale_banner);
        emptyText = findViewById(R.id.empty_text);
        RecyclerView list = findViewById(R.id.post_list);

        adapter = new PostAdapter(this::openDetail);
        LinearLayoutManager lm = new LinearLayoutManager(this);
        list.setLayoutManager(lm);
        list.setAdapter(adapter);
        list.addOnScrollListener(new RecyclerView.OnScrollListener() {
            @Override
            public void onScrolled(@NonNull RecyclerView rv, int dx, int dy) {
                // 마지막 3개 안쪽까지 오면 다음 페이지
                if (dy > 0 && lm.findLastVisibleItemPosition() >= adapter.getItemCount() - 3) {
                    loadNextPage();
                }
            }
        });
        refresh.setOnRefreshListener(this::reloadAll);

        setTitle(getString(R.string.list_title));
        reloadAll();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateStaleBanner();   // 화면에 돌아올 때 시간 경과를 다시 판정
    }

    /** 공간 목록(필터 선택지) → Post 목록 순서로 다시 불러온다. */
    private void reloadAll() {
        refresh.setRefreshing(true);
        api.spaces().enqueue(new Callback<Page<Space>>() {
            @Override
            public void onResponse(Call<Page<Space>> call, Response<Page<Space>> res) {
                if (handleAuthError(res.code())) return;
                if (res.isSuccessful() && res.body() != null && res.body().results != null) {
                    spaces.clear();
                    spaces.addAll(res.body().results);
                    setupSpinner();
                }
                loadFirstPage();
            }

            @Override
            public void onFailure(Call<Page<Space>> call, Throwable t) {
                Log.w("SpaceCheck", "request failed", t);
                loadFirstPage();
            }
        });
    }

    private void setupSpinner() {
        List<String> labels = new ArrayList<>();
        labels.add(getString(R.string.all_spaces));
        Map<Integer, String> names = new HashMap<>();
        int selectedIndex = 0;
        for (int i = 0; i < spaces.size(); i++) {
            Space s = spaces.get(i);
            labels.add(s.name);
            names.put(s.id, s.name);
            if (selectedSpaceId != null && selectedSpaceId == s.id) selectedIndex = i + 1;
        }
        adapter.setSpaceNames(names);
        spaceSpinner.setOnItemSelectedListener(null);
        spaceSpinner.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, labels));
        spaceSpinner.setSelection(selectedIndex, false);
        spaceSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) {
                Integer newId = pos == 0 ? null : spaces.get(pos - 1).id;
                if (newId == null ? selectedSpaceId != null : !newId.equals(selectedSpaceId)) {
                    selectedSpaceId = newId;      // 공간 필터 변경 → 첫 페이지부터 다시
                    refresh.setRefreshing(true);
                    loadFirstPage();
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
            }
        });
    }

    private void loadFirstPage() {
        loading = true;
        api.posts(selectedSpaceId).enqueue(new PageCallback(true));
    }

    private void loadNextPage() {
        if (loading || nextUrl == null) return;
        loading = true;
        api.postsPage(nextUrl).enqueue(new PageCallback(false));
    }

    private class PageCallback implements Callback<Page<Post>> {
        private final boolean first;

        PageCallback(boolean first) {
            this.first = first;
        }

        @Override
        public void onResponse(Call<Page<Post>> call, Response<Page<Post>> res) {
            loading = false;
            refresh.setRefreshing(false);
            if (handleAuthError(res.code())) return;
            if (!res.isSuccessful() || res.body() == null) {
                showEmpty(getString(R.string.server_error, res.code()));
                return;
            }
            List<Post> posts = res.body().results == null ? new ArrayList<>() : res.body().results;
            nextUrl = res.body().next;
            if (first) {
                adapter.replace(posts);
                updateStaleBanner();
            } else {
                adapter.append(posts);
            }
            if (adapter.getItemCount() == 0) showEmpty(getString(R.string.no_posts));
            else emptyText.setVisibility(View.GONE);
        }

        @Override
        public void onFailure(Call<Page<Post>> call, Throwable t) {
                Log.w("SpaceCheck", "request failed", t);
            loading = false;
            refresh.setRefreshing(false);
            showEmpty(getString(R.string.network_error));
        }
    }

    /**
     * 데이터 오래됨 안내. 목록은 최신순이므로 맨 위 Post 시각 = 현재 필터(전체/공간)의 최종 갱신 시각.
     * 10분(StaleChecker.STALE_MINUTES) 초과면 "데이터 오래됨 (최종 갱신 시각: …)" 을 빨간 바탕으로 표시.
     */
    private void updateStaleBanner() {
        if (adapter == null) return;
        Post newest = adapter.first();
        OffsetDateTime last = newest == null ? null : TimeUtil.parse(newest.publishedDate);
        staleBanner.setVisibility(View.VISIBLE);
        if (last == null) {
            staleBanner.setText(R.string.no_data_yet);
            staleBanner.setBackgroundColor(Color.parseColor("#888888"));
        } else if (StaleChecker.isStale(last, OffsetDateTime.now())) {
            staleBanner.setText(getString(R.string.stale_data, TimeUtil.format(last)));
            staleBanner.setBackgroundColor(Color.parseColor("#D33A2C"));
        } else {
            staleBanner.setText(getString(R.string.last_updated, TimeUtil.format(last)));
            staleBanner.setBackgroundColor(Color.parseColor("#2E9E4F"));
        }
    }

    private void showEmpty(String msg) {
        emptyText.setText(msg);
        emptyText.setVisibility(View.VISIBLE);
    }

    private void openDetail(Post post) {
        Intent i = new Intent(this, PostDetailActivity.class);
        i.putExtra(PostDetailActivity.EXTRA_ID, post.id);
        startActivity(i);
    }

    /** 401 이면 토큰 만료 → 로그인 화면으로. */
    private boolean handleAuthError(int code) {
        if (code != 401) return false;
        session.clearToken();
        Intent i = new Intent(this, LoginActivity.class);
        i.putExtra(LoginActivity.EXTRA_MESSAGE, getString(R.string.session_expired));
        startActivity(i);
        finish();
        return true;
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_list, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_refresh) {
            reloadAll();
            return true;
        }
        if (item.getItemId() == R.id.action_logout) {
            session.clearToken();
            Intent i = new Intent(this, LoginActivity.class);
            i.putExtra(LoginActivity.EXTRA_MESSAGE, getString(R.string.logged_out));
            startActivity(i);
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
