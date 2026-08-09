package com.example.connect.ui.screens

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.io.File

class RepositoryViewModel(application: Application) : AndroidViewModel(application) {
    private val _uiState = MutableStateFlow<RepositoryUiState>(RepositoryUiState.Loading)
    val uiState: StateFlow<RepositoryUiState> = _uiState.asStateFlow()

    private val _currentPath = MutableStateFlow(application.filesDir.absolutePath)
    val currentPath: StateFlow<String> = _currentPath.asStateFlow()

    init {
        // Create some dummy files if they don't exist to make the explorer useful
        createDummyFiles(application.filesDir)
        loadFiles(_currentPath.value)
    }

    private fun createDummyFiles(baseDir: File) {
        val osintDir = File(baseDir, "osint_data")
        if (!osintDir.exists()) osintDir.mkdirs()
        
        val scriptsDir = File(baseDir, "scripts")
        if (!scriptsDir.exists()) scriptsDir.mkdirs()

        File(osintDir, "scan_results_google_com.json").apply { if (!exists()) writeText("{}") }
        File(osintDir, "leak_report_admin.txt").apply { if (!exists()) writeText("No leaks found.") }
        File(scriptsDir, "nmap_basic.sh").apply { if (!exists()) writeText("#!/bin/bash\nnmap $1") }
        File(baseDir, "README.md").apply { if (!exists()) writeText("# OSINT Repository\nManage your scans here.") }
    }

    fun loadFiles(path: String) {
        viewModelScope.launch {
            _uiState.value = RepositoryUiState.Loading
            try {
                val directory = File(path)
                if (directory.exists() && directory.isDirectory) {
                    val files = directory.listFiles()?.map { 
                        FileItem(
                            name = it.name,
                            path = it.absolutePath,
                            isDirectory = it.isDirectory,
                            size = if (it.isDirectory) 0 else it.length(),
                            lastModified = it.lastModified()
                        )
                    }?.sortedWith(compareByDescending<FileItem> { it.isDirectory }.thenBy { it.name }) ?: emptyList()
                    
                    _uiState.value = RepositoryUiState.Success(files)
                    _currentPath.value = path
                } else {
                    _uiState.value = RepositoryUiState.Error("Directory does not exist")
                }
            } catch (e: Exception) {
                _uiState.value = RepositoryUiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun navigateBack() {
        val currentFile = File(_currentPath.value)
        val parent = currentFile.parentFile
        if (parent != null && parent.absolutePath.startsWith(getApplication<Application>().filesDir.absolutePath)) {
            loadFiles(parent.absolutePath)
        }
    }
}

data class FileItem(
    val name: String,
    val path: String,
    val isDirectory: Boolean,
    val size: Long,
    val lastModified: Long
)

sealed interface RepositoryUiState {
    data object Loading : RepositoryUiState
    data class Success(val files: List<FileItem>) : RepositoryUiState
    data class Error(val message: String) : RepositoryUiState
}
