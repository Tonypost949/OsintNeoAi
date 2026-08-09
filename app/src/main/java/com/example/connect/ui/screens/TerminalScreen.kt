package com.example.connect.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material.icons.rounded.Terminal
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.tooling.preview.Preview
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.connect.domain.model.OsintScript
import kotlinx.coroutines.launch

@Composable
fun TerminalScreen(
    scriptId: String? = null,
    modifier: Modifier = Modifier,
    viewModel: TerminalViewModel = viewModel(),
) {
    val terminalLines by viewModel.terminalLines.collectAsStateWithLifecycle()
    val scripts by viewModel.scripts.collectAsStateWithLifecycle()

    LaunchedEffect(scriptId, scripts) {
        if (scriptId != null && scripts.isNotEmpty()) {
            scripts.find { it.id == scriptId }?.let { viewModel.runScript(it) }
        }
    }
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()

    // Auto-scroll to bottom when new lines are added
    LaunchedEffect(terminalLines.size) {
        if (terminalLines.isNotEmpty()) {
            listState.animateScrollToItem(terminalLines.size - 1)
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFF0D0D0D)) // Darker background for terminal
    ) {
        // Terminal Header
        Surface(
            color = Color(0xFF1A1A1A),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Rounded.Terminal,
                    contentDescription = null,
                    tint = Color.Green,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "OSINT-NEOAI-TERMINAL",
                    style = MaterialTheme.typography.labelMedium.copy(
                        color = Color.Green,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 2.sp
                    )
                )
            }
        }

        // Script Suggestions
        if (scripts.isNotEmpty()) {
            LazyRow(
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.background(Color(0xFF151515))
            ) {
                items(scripts) { script ->
                    SuggestionChip(
                        onClick = { viewModel.runScript(script) },
                        label = {
                            Text(
                                text = "./${script.name}",
                                fontFamily = FontFamily.Monospace,
                                fontSize = 12.sp
                            )
                        },
                        colors = SuggestionChipDefaults.suggestionChipColors(
                            containerColor = Color.Transparent,
                            labelColor = Color.Green
                        ),
                        border = SuggestionChipDefaults.suggestionChipBorder(
                            borderColor = Color.Green.copy(alpha = 0.5f),
                            enabled = true
                        )
                    )
                }
            }
        }

        // Terminal Output
        LazyColumn(
            state = listState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            items(terminalLines) { line ->
                TerminalLineItem(line)
            }
        }

        // Terminal Input
        Surface(
            color = Color(0xFF1A1A1A),
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .padding(8.dp)
                    .fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = " > ",
                    color = Color.Green,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold
                )
                TextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = Color.Transparent,
                        unfocusedContainerColor = Color.Transparent,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent,
                        cursorColor = Color.Green,
                        focusedTextColor = Color.White
                    ),
                    textStyle = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 16.sp
                    ),
                    placeholder = {
                        Text(
                            "Type command or ./script...",
                            color = Color.Gray,
                            fontFamily = FontFamily.Monospace,
                            fontSize = 14.sp
                        )
                    },
                    keyboardOptions = KeyboardOptions(
                        imeAction = ImeAction.Done
                    ),
                    keyboardActions = KeyboardActions(
                        onDone = {
                            if (inputText.isNotBlank()) {
                                viewModel.executeCommand(inputText)
                                inputText = ""
                            }
                        }
                    ),
                    singleLine = true
                )
                IconButton(
                    onClick = {
                        if (inputText.isNotBlank()) {
                            viewModel.executeCommand(inputText)
                            inputText = ""
                        }
                    }
                ) {
                    Icon(
                        imageVector = Icons.Rounded.PlayArrow,
                        contentDescription = "Run",
                        tint = Color.Green
                    )
                }
            }
        }
    }
}

@Composable
fun TerminalLineItem(line: TerminalLine) {
    val color = when (line.type) {
        TerminalLineType.COMMAND -> Color.Cyan
        TerminalLineType.OUTPUT -> Color.White
        TerminalLineType.SYSTEM -> Color.Green
        TerminalLineType.ERROR -> Color.Red
    }

    Text(
        text = line.text,
        color = color,
        fontFamily = FontFamily.Monospace,
        fontSize = 14.sp,
        modifier = Modifier.padding(vertical = 2.dp),
        lineHeight = 18.sp
    )
}

@Preview(showBackground = true, device = "spec:width=411dp,height=891dp")
@Composable
fun TerminalScreenPreview() {
    MaterialTheme {
        TerminalScreen()
    }
}
