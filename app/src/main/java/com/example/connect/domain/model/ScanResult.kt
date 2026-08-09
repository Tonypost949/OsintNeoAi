package com.example.connect.domain.model

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class ScanResult(
    val id: String,
    val target: String,
    val status: ScanStatus,
    val findings: List<String>,
    val timestamp: Long
)
