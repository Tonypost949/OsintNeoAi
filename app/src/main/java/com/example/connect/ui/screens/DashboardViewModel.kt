package com.example.connect.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.connect.data.remote.NetworkModule
import com.example.connect.domain.model.OsintScript
import com.example.connect.domain.model.ScanResult
import com.example.connect.domain.model.ScanStatus
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

import kotlin.time.Duration.Companion.seconds

class DashboardViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<DashboardUiState>(DashboardUiState.Loading)
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()

    private var isPolling = false

    init {
        startPolling()
    }

    private fun startPolling() {
        if (isPolling) return
        isPolling = true
        viewModelScope.launch {
            while (isPolling) {
                fetchData(showLoading = _uiState.value is DashboardUiState.Loading)
                delay(5.seconds) // Poll every 5 seconds
            }
        }
    }

    fun fetchData(showLoading: Boolean = true) {
        viewModelScope.launch {
            if (showLoading) {
                _uiState.value = DashboardUiState.Loading
            }
            try {
                val scans = NetworkModule.apiService.getScanResults()
                val scripts = NetworkModule.apiService.getScripts()
                
                val activeScans = scans.filter { 
                    it.status == ScanStatus.RUNNING || it.status == ScanStatus.PENDING 
                }
                val recentScans = scans.filter { 
                    it.status == ScanStatus.COMPLETED || it.status == ScanStatus.FAILED 
                }.sortedByDescending { it.timestamp }

                _uiState.value = DashboardUiState.Success(
                    activeScans = activeScans,
                    recentScans = recentScans,
                    scripts = scripts
                )
            } catch (e: Exception) {
                val errorMessage = when {
                    e.message?.contains("502") == true -> "Backend Error: 502 Bad Gateway. Please try again later."
                    e.message?.contains("503") == true || e.message?.contains("504") == true -> 
                        "Waking up cloud server... (Render free tier takes ~30s)"
                    else -> e.message ?: "Unknown error"
                }
                _uiState.value = DashboardUiState.Error(errorMessage)
            }
        }
    }

    override fun onCleared() {
        isPolling = false
    }
}

sealed interface DashboardUiState {
    data object Loading : DashboardUiState
    data class Success(
        val activeScans: List<ScanResult>,
        val recentScans: List<ScanResult>,
        val scripts: List<OsintScript>
    ) : DashboardUiState
    data class Error(val message: String) : DashboardUiState
}
