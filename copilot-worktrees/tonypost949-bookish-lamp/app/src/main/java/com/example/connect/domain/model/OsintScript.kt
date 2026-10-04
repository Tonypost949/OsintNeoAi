package com.example.connect.domain.model

import com.squareup.moshi.JsonClass

@JsonClass(generateAdapter = true)
data class OsintScript(
    val id: String,
    val name: String,
    val description: String,
    val version: String,
    val author: String
)
