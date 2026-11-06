package tz.agripocket.kodimahiri;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import android.view.View;
import android.os.Build;

import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.IOException;

public class MainActivity extends Activity {
    private WebView webView;
    private static final int MIC_REQ = 2101;
    private boolean serverStarted = false;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> {
                    String origin = request.getOrigin().toString();
                    if (origin.contains("127.0.0.1") || origin.contains("localhost")) {
                        if (Build.VERSION.SDK_INT >= 23 &&
                            checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                            requestMicPermission();
                            request.deny();
                        } else {
                            request.grant(request.getResources());
                        }
                    } else {
                        request.deny();
                    }
                });
            }
        });

        startEmbeddedBackend();
    }

    private void startEmbeddedBackend() {
        try {
            File home = new File(getFilesDir(), "kodi-mahiri");
            copyAssets("kodi-mahiri", home);
            if (!Python.isStarted()) Python.start(new AndroidPlatform(this));
            Python.getInstance().getModule("android_server").callAttr("start", home.getAbsolutePath(), 8765);
            serverStarted = true;
            webView.postDelayed(() -> webView.loadUrl("http://127.0.0.1:8765/"), 2000);
        } catch (Exception e) {
            Toast.makeText(this, "Imeshindwa kuwasha injini: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void requestMicPermission() {
        if (Build.VERSION.SDK_INT >= 23 &&
            checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, MIC_REQ);
        }
    }

    private void copyAssets(String assetPath, File outDir) throws IOException {
        if (!outDir.exists() && !outDir.mkdirs()) throw new IOException("Haiwezi kuunda folda ya data");
        String[] children = getAssets().list(assetPath);
        if (children == null || children.length == 0) {
            File out = new File(outDir.getParentFile(), outDir.getName());
            try (InputStream in = getAssets().open(assetPath);
                 FileOutputStream fos = new FileOutputStream(out)) {
                byte[] buffer = new byte[8192]; int n;
                while ((n = in.read(buffer)) > 0) fos.write(buffer, 0, n);
            }
            return;
        }
        for (String child : children) {
            String childAsset = assetPath + "/" + child;
            String[] nested = getAssets().list(childAsset);
            File target = new File(outDir, child);
            if (nested != null && nested.length > 0) copyAssets(childAsset, target);
            else {
                try (InputStream in = getAssets().open(childAsset);
                     FileOutputStream fos = new FileOutputStream(target)) {
                    byte[] buffer = new byte[8192]; int n;
                    while ((n = in.read(buffer)) > 0) fos.write(buffer, 0, n);
                }
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
