package com.example.connect.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.connect.data.remote.NetworkModule
import com.example.connect.domain.model.ScanResult
import com.example.connect.domain.model.ScanStatus
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlin.time.Duration.Companion.seconds

class DashboardDetailViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<DashboardDetailUiState>(DashboardDetailUiState.Loading)
    val uiState: StateFlow<DashboardDetailUiState> = _uiState.asStateFlow()

    private var pollingJob: Job? = null

    fun fetchScanDetail(id: String) {
        pollingJob?.cancel()
        pollingJob = viewModelScope.launch {
            var firstLoad = true
            while (true) {
                if (firstLoad) {
                    _uiState.value = DashboardDetailUiState.Loading
                }
                try {
                    val result = NetworkModule.apiService.getScanById(id)
                    _uiState.value = DashboardDetailUiState.Success(result)
                    
                    // If scan is finished, stop polling
                    if (result.status == ScanStatus.COMPLETED || result.status == ScanStatus.FAILED) {
                        break
                    }
                } catch (e: Exception) {
                    val errorMessage = when {
                        e.message?.contains("502") == true -> "Backend Error: 502 Bad Gateway. Polling stopped."
                        else -> e.message ?: "Unknown error"
                    }
                    _uiState.value = DashboardDetailUiState.Error(errorMessage)
                    break
                }
                firstLoad = false
                delay(3.seconds) // Poll more frequently for detail (3s)
            }
        }
    }

    override fun onCleared() {
        pollingJob?.cancel()
    }
}

sealed interface DashboardDetailUiState {
    object Loading : DashboardDetailUiState
    data class Success(val scan: ScanResult) : DashboardDetailUiState
    data class Error(val message: String) : DashboardDetailUiState
}
