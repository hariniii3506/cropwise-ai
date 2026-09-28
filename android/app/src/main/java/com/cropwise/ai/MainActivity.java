package com.cropwise.ai;

import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import androidx.activity.OnBackPressedCallback;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Ensure Cookies (Flask session cookies) are enabled and persistent
        try {
            CookieManager cookieManager = CookieManager.getInstance();
            cookieManager.setAcceptCookie(true);
            WebView webView = getBridge().getWebView();
            if (webView != null) {
                cookieManager.setAcceptThirdPartyCookies(webView, true);
                WebSettings settings = webView.getSettings();
                settings.setDomStorageEnabled(true);
                settings.setDatabaseEnabled(true);
                settings.setJavaScriptEnabled(true);
            }
        } catch (Exception ignored) {
        }

        // Handle natural Android hardware & gesture back button navigation
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                try {
                    WebView webView = getBridge().getWebView();
                    if (webView != null && webView.canGoBack()) {
                        webView.goBack();
                        return;
                    }
                } catch (Exception ignored) {
                }
                setEnabled(false);
                getOnBackPressedDispatcher().onBackPressed();
            }
        });
    }
}

