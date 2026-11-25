package kr.ac.khu.spacecheck;

import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import kr.ac.khu.spacecheck.model.TokenResponse;
import kr.ac.khu.spacecheck.net.ApiClient;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * 로그인 화면. 서버를 고르고 아이디·비밀번호를 입력하면 /api-token-auth/ 로 토큰을 받아 저장한다.
 * 비밀번호는 요청에만 쓰고 저장하지 않는다.
 */
public class LoginActivity extends AppCompatActivity {
    public static final String EXTRA_MESSAGE = "message";
    /** Android 17(API 37) 의 로컬 네트워크 접근 권한 (사설 IP 10.0.2.2 접속에 필요). */
    private static final String PERM_LOCAL_NETWORK = "android.permission.ACCESS_LOCAL_NETWORK";
    private static final int REQ_LOCAL_NETWORK = 1;

    private Session session;
    private Spinner serverSpinner;
    private EditText usernameInput;
    private EditText passwordInput;
    private Button loginButton;
    private ProgressBar progress;
    private TextView messageText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        session = new Session(this);
        if (session.isLoggedIn() && getIntent().getStringExtra(EXTRA_MESSAGE) == null) {
            openList();   // 이미 토큰이 있으면 바로 목록으로
            return;
        }
        setContentView(R.layout.activity_login);
        SystemBars.setup(this, R.id.root, R.id.toolbar);
        serverSpinner = findViewById(R.id.server_spinner);
        usernameInput = findViewById(R.id.username_input);
        passwordInput = findViewById(R.id.password_input);
        loginButton = findViewById(R.id.login_button);
        progress = findViewById(R.id.login_progress);
        messageText = findViewById(R.id.login_message);

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_dropdown_item, ServerConfig.LABELS);
        serverSpinner.setAdapter(adapter);
        serverSpinner.setSelection(ServerConfig.indexOf(session.getServer()));
        usernameInput.setText(session.getUsername());

        String msg = getIntent().getStringExtra(EXTRA_MESSAGE);
        if (msg != null) showMessage(msg);

        loginButton.setOnClickListener(v -> tryLogin());
    }

    private void tryLogin() {
        String username = usernameInput.getText().toString().trim();
        String password = passwordInput.getText().toString();
        if (username.isEmpty() || password.isEmpty()) {
            showMessage(getString(R.string.login_empty));
            return;
        }
        String server = ServerConfig.URLS[serverSpinner.getSelectedItemPosition()];
        if (needsLocalNetworkPermission(server)) {
            // 권한 창을 띄우고, 허용되면 onRequestPermissionsResult 에서 다시 로그인 시도
            ActivityCompat.requestPermissions(this, new String[]{PERM_LOCAL_NETWORK}, REQ_LOCAL_NETWORK);
            return;
        }
        setBusy(true);
        ApiClient.create(server, null).login(username, password).enqueue(new Callback<TokenResponse>() {
            @Override
            public void onResponse(Call<TokenResponse> call, Response<TokenResponse> res) {
                setBusy(false);
                if (res.isSuccessful() && res.body() != null && res.body().token != null) {
                    passwordInput.setText("");
                    session.saveLogin(server, username, res.body().token);
                    openList();
                } else if (res.code() == 400) {
                    showMessage(getString(R.string.login_wrong));     // 아이디/비밀번호 틀림
                } else {
                    showMessage(getString(R.string.server_error, res.code()));
                }
            }

            @Override
            public void onFailure(Call<TokenResponse> call, Throwable t) {
                Log.w("SpaceCheck", "request failed", t);
                setBusy(false);
                showMessage(getString(R.string.network_error));
            }
        });
    }

    /** 로컬 서버(10.0.2.2)를 골랐고, API 37 이상이며, 아직 권한이 없을 때만 true. 온라인 서버는 필요 없음. */
    private boolean needsLocalNetworkPermission(String server) {
        return ServerConfig.LOCAL.equals(server)
                && Build.VERSION.SDK_INT >= 37
                && ContextCompat.checkSelfPermission(this, PERM_LOCAL_NETWORK) != PackageManager.PERMISSION_GRANTED;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_LOCAL_NETWORK) return;
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            tryLogin();
        } else {
            showMessage(getString(R.string.local_network_denied));
        }
    }

    private void openList() {
        startActivity(new Intent(this, PostListActivity.class));
        finish();
    }

    private void setBusy(boolean busy) {
        loginButton.setEnabled(!busy);
        progress.setVisibility(busy ? View.VISIBLE : View.GONE);
    }

    private void showMessage(String msg) {
        messageText.setText(msg);
        messageText.setVisibility(View.VISIBLE);
    }
}
