package com.example.connect.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.Error
import androidx.compose.material.icons.rounded.Pending
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.SuggestionChip
import androidx.compose.material3.SuggestionChipDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.connect.domain.model.OsintScript
import com.example.connect.domain.model.ScanResult
import com.example.connect.domain.model.ScanStatus
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import androidx.compose.ui.tooling.preview.Preview
import com.example.connect.ui.theme.ConnectTheme

@Preview(showBackground = true, showSystemUi = true)
@Composable
private fun DashboardScreenPreview() {
    ConnectTheme {
        DashboardContent(
            activeScans = listOf(
                ScanResult("1", "google.com", ScanStatus.RUNNING, emptyList(), System.currentTimeMillis())
            ),
            recentScans = listOf(
                ScanResult("2", "example.com", ScanStatus.COMPLETED, listOf("Finding 1"), System.currentTimeMillis() - 3600000)
            ),
            scripts = listOf(
                OsintScript("1", "Basic Scan", "Basic nmap scan", "1.0", "Admin")
            ),
            onItemClick = {},
            onScriptClick = {}
        )
    }
}

@Composable
fun DashboardScreen(
    onItemClick: (String) -> Unit,
    onScriptClick: (String) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: DashboardViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Box(modifier = modifier.fillMaxSize()) {
        when (val state = uiState) {
            is DashboardUiState.Loading -> {
                CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
            }
            is DashboardUiState.Error -> {
                Text(
                    text = "Error: ${state.message}",
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.align(Alignment.Center).padding(16.dp)
                )
            }
            is DashboardUiState.Success -> {
                DashboardContent(
                    activeScans = state.activeScans,
                    recentScans = state.recentScans,
                    scripts = state.scripts,
                    onItemClick = onItemClick,
                    onScriptClick = onScriptClick
                )
            }
        }
    }
}

@Composable
private fun DashboardContent(
    activeScans: List<ScanResult>,
    recentScans: List<ScanResult>,
    scripts: List<OsintScript>,
    onItemClick: (String) -> Unit,
    onScriptClick: (String) -> Unit
) {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        if (activeScans.isNotEmpty()) {
            item {
                SectionHeader("Active Scans")
            }
            items(activeScans, key = { "active-${it.id}" }) { scan ->
                ScanItem(scan = scan, onClick = { onItemClick(scan.id) })
                HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
            }
        }

        item {
            SectionHeader("Recent Scans")
        }
        if (recentScans.isEmpty()) {
            item {
                EmptyState("No recent scans found")
            }
        } else {
            items(recentScans, key = { "recent-${it.id}" }) { scan ->
                ScanItem(scan = scan, onClick = { onItemClick(scan.id) })
                HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
            }
        }

        item {
            SectionHeader("Available Scripts")
        }
        items(scripts, key = { "script-${it.id}" }) { script ->
            ListItem(
                headlineContent = { Text(script.name) },
                supportingContent = { Text(script.description) },
                trailingContent = { Text("v${script.version}", style = MaterialTheme.typography.labelSmall) },
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onScriptClick(script.id) }
            )
            HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
        }
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleLarge,
        color = MaterialTheme.colorScheme.primary,
        modifier = Modifier.padding(start = 16.dp, top = 24.dp, end = 16.dp, bottom = 8.dp)
    )
}

@Composable
private fun ScanItem(scan: ScanResult, onClick: () -> Unit) {
    ListItem(
        headlineContent = { Text(scan.target) },
        supportingContent = {
            StatusChip(status = scan.status)
        },
        trailingContent = {
            val date = Date(scan.timestamp)
            val formatter = SimpleDateFormat("MMM dd, HH:mm", Locale.getDefault())
            Text(formatter.format(date), style = MaterialTheme.typography.labelMedium)
        },
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    )
}

@Composable
private fun StatusChip(status: ScanStatus) {
    val (icon, color, label) = when (status) {
        ScanStatus.PENDING -> Triple(Icons.Rounded.Pending, Color.Gray, "Pending")
        ScanStatus.RUNNING -> Triple(Icons.Rounded.PlayArrow, MaterialTheme.colorScheme.secondary, "Running")
        ScanStatus.COMPLETED -> Triple(Icons.Rounded.CheckCircle, Color(0xFF4CAF50), "Completed")
        ScanStatus.FAILED -> Triple(Icons.Rounded.Error, MaterialTheme.colorScheme.error, "Failed")
    }

    SuggestionChip(
        onClick = { },
        label = { Text(label) },
        icon = {
            if (status == ScanStatus.RUNNING) {
                CircularProgressIndicator(
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp,
                    color = color
                )
            } else {
                Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp), tint = color)
            }
        },
        colors = SuggestionChipDefaults.suggestionChipColors(
            labelColor = color
        ),
        border = SuggestionChipDefaults.suggestionChipBorder(
            enabled = true,
            borderColor = color.copy(alpha = 0.5f)
        )
    )
}

@Composable
private fun EmptyState(message: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 32.dp, horizontal = 16.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(text = message, style = MaterialTheme.typography.bodyMedium, color = Color.Gray)
    }
}
