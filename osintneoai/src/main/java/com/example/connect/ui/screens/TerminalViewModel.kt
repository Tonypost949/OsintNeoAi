package com.example.connect.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.connect.data.remote.NetworkModule
import com.example.connect.domain.model.OsintScript
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlin.time.Duration.Companion.milliseconds

class TerminalViewModel : ViewModel() {
    private val _terminalLines = MutableStateFlow<List<TerminalLine>>(
        listOf(TerminalLine("Welcome to OSINT NeoAI Terminal v1.0.0", TerminalLineType.SYSTEM))
    )
    val terminalLines: StateFlow<List<TerminalLine>> = _terminalLines.asStateFlow()

    private val _scripts = MutableStateFlow<List<OsintScript>>(emptyList())
    val scripts: StateFlow<List<OsintScript>> = _scripts.asStateFlow()

    init {
        fetchScripts()
    }

    private fun fetchScripts() {
        viewModelScope.launch {
            try {
                val fetchedScripts = NetworkModule.apiService.getScripts()
                _scripts.value = fetchedScripts
            } catch (e: Exception) {
                val errorMsg = when {
                    e.message?.contains("502") == true -> "502 Bad Gateway"
                    e.message?.contains("503") == true || e.message?.contains("504") == true -> 
                        "Waking up cloud server... (Render free tier takes ~30s)"
                    else -> e.message
                }
                addLog("Failed to fetch scripts: $errorMsg", TerminalLineType.ERROR)
            }
        }
    }

    fun executeCommand(command: String) {
        if (command.isBlank()) return

        addLog("connect@system:~$ $command", TerminalLineType.COMMAND)

        when {
            command.startsWith("./") -> {
                val scriptName = command.removePrefix("./")
                val script = _scripts.value.find { it.name.equals(scriptName, ignoreCase = true) }
                if (script != null) {
                    runScript(script)
                } else {
                    addLog("Script not found: $scriptName", TerminalLineType.ERROR)
                }
            }
            command == "help" -> {
                addLog("Available commands:", TerminalLineType.SYSTEM)
                addLog("  help              - Show this help message", TerminalLineType.SYSTEM)
                addLog("  list              - List available scripts", TerminalLineType.SYSTEM)
                addLog("  clear             - Clear the terminal", TerminalLineType.SYSTEM)
                addLog("  ./<script_name>   - Execute a script", TerminalLineType.SYSTEM)
            }
            command == "list" -> {
                addLog("Available scripts:", TerminalLineType.SYSTEM)
                _scripts.value.forEach { 
                    addLog("  ./${it.name} - ${it.description}", TerminalLineType.SYSTEM)
                }
            }
            command == "clear" -> {
                _terminalLines.value = listOf(TerminalLine("Terminal cleared.", TerminalLineType.SYSTEM))
            }
            else -> {
                addLog("Command not found: $command", TerminalLineType.ERROR)
            }
        }
    }

    fun runScript(script: OsintScript) {
        addLog("Executing script: ${script.name}...", TerminalLineType.SYSTEM)
        
        viewModelScope.launch {
            // Mocking real-time execution output
            // In a real app, this would be a network call returning a stream
            try {
                // Simulating network delay and streaming output
                addLog("Initializing ${script.name} engine...", TerminalLineType.OUTPUT)
                delay(800.milliseconds)
                addLog("Target acquisition in progress...", TerminalLineType.OUTPUT)
                delay(1200.milliseconds)
                addLog("[INFO] Connecting to external databases...", TerminalLineType.OUTPUT)
                delay(1000.milliseconds)
                addLog("[SUCCESS] Database connection established.", TerminalLineType.OUTPUT)
                delay(500.milliseconds)
                addLog("Running modules for ${script.name}...", TerminalLineType.OUTPUT)
                
                repeat(5) { i ->
                    delay(700.milliseconds)
                    addLog("[DATA] Processing chunk ${i + 1}/5...", TerminalLineType.OUTPUT)
                }
                
                delay(1000.milliseconds)
                addLog("Execution completed successfully.", TerminalLineType.SYSTEM)
                addLog("connect@system:~$ ", TerminalLineType.COMMAND)
            } catch (e: Exception) {
                addLog("Execution failed: ${e.message}", TerminalLineType.ERROR)
            }
        }
    }

    private fun addLog(text: String, type: TerminalLineType) {
        _terminalLines.value = _terminalLines.value + TerminalLine(text, type)
    }
}

data class TerminalLine(
    val text: String,
    val type: TerminalLineType
)

enum class TerminalLineType {
    COMMAND,
    OUTPUT,
    SYSTEM,
    ERROR
}
