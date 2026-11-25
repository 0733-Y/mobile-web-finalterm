package kr.ac.khu.spacecheck;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import kr.ac.khu.spacecheck.model.Post;
import kr.ac.khu.spacecheck.net.ApiClient;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/** Post 상세 화면: GET /api_root/Post/{id}/ 로 한 건을 받아 큰 이미지와 정보를 보여준다. 2-4 / 3-2 */
public class PostDetailActivity extends AppCompatActivity {
    public static final String EXTRA_ID = "post_id";

    private Session session;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_post_detail);
        SystemBars.setup(this, R.id.root, R.id.toolbar);
        if (getSupportActionBar() != null) getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        setTitle(R.string.detail_title);
        session = new Session(this);

        int id = getIntent().getIntExtra(EXTRA_ID, -1);
        ProgressBar progress = findViewById(R.id.detail_progress);
        TextView error = findViewById(R.id.detail_error);
        progress.setVisibility(View.VISIBLE);

        ApiClient.create(session.getServer(), session.getToken()).post(id).enqueue(new Callback<Post>() {
            @Override
            public void onResponse(Call<Post> call, Response<Post> res) {
                progress.setVisibility(View.GONE);
                if (res.code() == 401) {
                    session.clearToken();
                    Intent i = new Intent(PostDetailActivity.this, LoginActivity.class);
                    i.putExtra(LoginActivity.EXTRA_MESSAGE, getString(R.string.session_expired));
                    startActivity(i);
                    finishAffinity();
                    return;
                }
                if (!res.isSuccessful() || res.body() == null) {
                    error.setText(getString(R.string.server_error, res.code()));
                    error.setVisibility(View.VISIBLE);
                    return;
                }
                show(res.body());
            }

            @Override
            public void onFailure(Call<Post> call, Throwable t) {
                Log.w("SpaceCheck", "request failed", t);
                progress.setVisibility(View.GONE);
                error.setText(R.string.network_error);
                error.setVisibility(View.VISIBLE);
            }
        });
    }

    private void show(Post p) {
        ImageView image = findViewById(R.id.detail_image);
        ((TextView) findViewById(R.id.detail_title)).setText(p.title);
        ((TextView) findViewById(R.id.detail_people)).setText(getString(R.string.people_count, p.personCount));
        PostAdapter.bindLevel(findViewById(R.id.detail_level), p.level);
        ((TextView) findViewById(R.id.detail_time)).setText(
                getString(R.string.updated_at, TimeUtil.format(TimeUtil.parse(p.publishedDate))));
        ((TextView) findViewById(R.id.detail_text)).setText(p.text == null ? "" : p.text);
        ImageLoader.load(p.image, image);
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }
}
