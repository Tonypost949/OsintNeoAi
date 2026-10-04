package com.example.connect.data.remote

import com.example.connect.domain.model.OsintScript
import com.example.connect.domain.model.ScanResult
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ConnectApiService {
    @GET("scripts")
    suspend fun getScripts(): List<OsintScript>

    @GET("scans")
    suspend fun getScanResults(@Query("target") target: String? = null): List<ScanResult>

    @GET("scans/{id}")
    suspend fun getScanById(@Path("id") id: String): ScanResult

    @POST("scripts/{id}/execute")
    suspend fun executeScript(@Path("id") id: String): okhttp3.ResponseBody
}
