package com.example.myapplication

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.webkit.WebViewClient
import android.webkit.WebChromeClient
import kotlinx.android.synthetic.main.activity_main.webView

class MainActivity : AppCompatActivity() {

    private val BASE_URL = "https://www.hola.com/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_main)
        // webView
        webView.webChromeClient = object : WebChromeClient(){

        }
        webView.webViewClient = object : WebViewClient(){

        }
        val settings = webView.settings
        settings.javaScriptEnabled = true

        webView.loadUrl(BASE_URL)
    }

    override fun onBackPressed() {
        if (webView.canGoBack()){
            webView.goBack()
        }else{
            super.onBackPressed()
        }
    }
}