package com.example.connect.data.remote

import com.example.connect.BuildConfig
import okhttp3.Interceptor
import okhttp3.Response

class ApiKeyInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val requestWithApiKey = originalRequest.newBuilder()
            .header("X-API-KEY", BuildConfig.CONNECT_API_KEY)
            .build()
        return chain.proceed(requestWithApiKey)
    }
}
