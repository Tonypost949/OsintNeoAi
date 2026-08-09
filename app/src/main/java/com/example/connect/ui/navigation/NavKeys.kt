package com.example.connect.ui.navigation

import androidx.navigation3.runtime.NavKey
import kotlinx.serialization.Serializable

sealed interface ConnectRoute : NavKey

@Serializable
data object Dashboard : ConnectRoute

@Serializable
data class DashboardDetail(val id: String) : ConnectRoute

@Serializable
data class Terminal(val scriptId: String? = null) : ConnectRoute

@Serializable
data object Repository : ConnectRoute

@Serializable
data class RepositoryDetail(val name: String) : ConnectRoute
