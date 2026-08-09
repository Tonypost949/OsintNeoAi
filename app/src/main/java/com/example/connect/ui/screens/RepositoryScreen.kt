package com.example.connect.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Folder
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.connect.ui.theme.ConnectTheme
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun RepositoryScreen(
    onRepoClick: (String) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: RepositoryViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val currentPath by viewModel.currentPath.collectAsStateWithLifecycle()

    Column(modifier = modifier.fillMaxSize()) {
        RepositoryHeader(
            currentPath = currentPath,
            onBackClick = { viewModel.navigateBack() }
        )
        
        Box(modifier = Modifier.weight(1f)) {
            when (val state = uiState) {
                is RepositoryUiState.Loading -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
                is RepositoryUiState.Error -> {
                    Text(
                        text = "Error: ${state.message}",
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.align(Alignment.Center).padding(16.dp)
                    )
                }
                is RepositoryUiState.Success -> {
                    FileList(
                        files = state.files,
                        onFileClick = { file ->
                            if (file.isDirectory) {
                                viewModel.loadFiles(file.path)
                            } else {
                                onRepoClick(file.name)
                            }
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun RepositoryHeader(
    currentPath: String,
    onBackClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(onClick = onBackClick) {
            Icon(Icons.AutoMirrored.Rounded.ArrowBack, contentDescription = "Back")
        }
        Column {
            Text(
                text = "Repository",
                style = MaterialTheme.typography.headlineSmall
            )
            Text(
                text = currentPath,
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
private fun FileList(
    files: List<FileItem>,
    onFileClick: (FileItem) -> Unit
) {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        items(files, key = { it.path }) { file ->
            ListItem(
                headlineContent = { Text(file.name) },
                supportingContent = {
                    if (!file.isDirectory) {
                        val date = Date(file.lastModified)
                        val formatter = SimpleDateFormat("MMM dd, HH:mm", Locale.getDefault())
                        Text("${formatSize(file.size)} • ${formatter.format(date)}")
                    }
                },
                leadingContent = {
                    Icon(
                        imageVector = if (file.isDirectory) Icons.Rounded.Folder else Icons.Rounded.Description,
                        contentDescription = null,
                        tint = if (file.isDirectory) MaterialTheme.colorScheme.primary else Color.Gray
                    )
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onFileClick(file) }
            )
            HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
        }
    }
}

private fun formatSize(size: Long): String {
    if (size <= 0) return "0 B"
    val units = listOf("B", "KB", "MB", "GB", "TB")
    val digitGroups = (Math.log10(size.toDouble()) / Math.log10(1024.0)).toInt()
    return String.format(Locale.US, "%.1f %s", size / Math.pow(1024.0, digitGroups.toDouble()), units[digitGroups])
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
private fun RepositoryScreenPreview() {
    ConnectTheme {
        Column(modifier = Modifier.fillMaxSize()) {
            RepositoryHeader(currentPath = "/storage/emulated/0/Android/data/com.example.connect/files", onBackClick = {})
            FileList(
                files = listOf(
                    FileItem("osint_data", "/path/to/osint_data", true, 0, System.currentTimeMillis()),
                    FileItem("report.json", "/path/to/report.json", false, 1024, System.currentTimeMillis())
                ),
                onFileClick = {}
            )
        }
    }
}
