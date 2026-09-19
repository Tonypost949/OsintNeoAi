package com.example.connect.ui

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Dashboard
import androidx.compose.material.icons.rounded.Storage
import androidx.compose.material.icons.rounded.Terminal
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationRail
import androidx.compose.material3.NavigationRailItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi
import androidx.compose.material3.adaptive.currentWindowAdaptiveInfo
import androidx.compose.material3.adaptive.navigation.BackNavigationBehavior
import androidx.compose.material3.adaptive.navigation3.ListDetailSceneStrategy
import androidx.compose.material3.adaptive.navigation3.SupportingPaneSceneStrategy
import androidx.compose.material3.adaptive.navigation3.rememberListDetailSceneStrategy
import androidx.compose.material3.adaptive.navigation3.rememberSupportingPaneSceneStrategy
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.lifecycle.compose.dropUnlessResumed
import androidx.navigation3.runtime.NavKey
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import androidx.window.core.layout.WindowWidthSizeClass
import com.example.connect.ui.navigation.ConnectRoute
import com.example.connect.ui.navigation.Dashboard
import com.example.connect.ui.navigation.DashboardDetail
import com.example.connect.ui.navigation.Repository
import com.example.connect.ui.navigation.RepositoryDetail
import com.example.connect.ui.navigation.Terminal
import com.example.connect.ui.screens.DashboardDetailScreen
import com.example.connect.ui.screens.DashboardScreen
import com.example.connect.ui.screens.RepositoryDetailScreen
import com.example.connect.ui.screens.RepositoryScreen
import com.example.connect.ui.screens.TerminalScreen

@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun ConnectApp() {
    val backStack = rememberNavBackStack(Dashboard)
    val adaptiveInfo = currentWindowAdaptiveInfo()
    val isExpanded = adaptiveInfo.windowSizeClass.windowWidthSizeClass == WindowWidthSizeClass.EXPANDED

    val listDetailStrategy = rememberListDetailSceneStrategy<NavKey>()
    val supportingPaneStrategy = rememberSupportingPaneSceneStrategy<NavKey>(
        backNavigationBehavior = BackNavigationBehavior.PopUntilCurrentDestinationChange
    )

    Scaffold(
        bottomBar = {
            if (!isExpanded) {
                ConnectBottomBar(
                    currentRoute = backStack.lastOrNull() as? ConnectRoute ?: Dashboard,
                    onNavigate = { route ->
                        backStack.clear()
                        backStack.add(route)
                    }
                )
            }
        }
    ) { innerPadding ->
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            if (isExpanded) {
                ConnectNavigationRail(
                    currentRoute = backStack.lastOrNull() as? ConnectRoute ?: Dashboard,
                    onNavigate = { route ->
                        backStack.clear()
                        backStack.add(route)
                    }
                )
            }

            NavDisplay(
                backStack = backStack,
                onBack = { backStack.removeLastOrNull() },
                sceneStrategies = listOf(listDetailStrategy, supportingPaneStrategy),
                entryProvider = entryProvider<NavKey> {
                    // List-Detail Destinations
                    entry<Dashboard>(
                        metadata = ListDetailSceneStrategy.listPane()
                    ) {
                        DashboardScreen(
                            onItemClick = { id ->
                                // For List-Detail, we usually want to replace the current detail if it exists
                                val detailEntries = backStack.filterIsInstance<DashboardDetail>()
                                detailEntries.forEach { backStack.remove(it) }
                                backStack.add(DashboardDetail(id))
                            },
                            onScriptClick = { scriptId ->
                                backStack.add(Terminal(scriptId))
                            }
                        )
                    }
                    entry<DashboardDetail>(
                        metadata = ListDetailSceneStrategy.detailPane()
                    ) { detail ->
                        DashboardDetailScreen(
                            id = detail.id,
                            onBack = { backStack.removeLastOrNull() },
                            showBackButton = !isExpanded
                        )
                    }

                    // Supporting Pane Destinations
                    entry<Repository>(
                        metadata = SupportingPaneSceneStrategy.mainPane()
                    ) {
                        RepositoryScreen(
                            onRepoClick = { name ->
                                val detailEntries = backStack.filterIsInstance<RepositoryDetail>()
                                detailEntries.forEach { backStack.remove(it) }
                                backStack.add(RepositoryDetail(name))
                            }
                        )
                    }
                    entry<RepositoryDetail>(
                        metadata = SupportingPaneSceneStrategy.supportingPane()
                    ) { detail ->
                        RepositoryDetailScreen(name = detail.name)
                    }

                    // Standard Destinations
                    entry<Terminal> { terminal ->
                        TerminalScreen(scriptId = terminal.scriptId)
                    }
                },
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun ConnectBottomBar(
    currentRoute: ConnectRoute,
    onNavigate: (ConnectRoute) -> Unit
) {
    NavigationBar {
        val items = listOf(
            NavigationItem("Dashboard", Icons.Rounded.Dashboard, Dashboard),
            NavigationItem("Terminal", Icons.Rounded.Terminal, Terminal()),
            NavigationItem("Repository", Icons.Rounded.Storage, Repository)
        )

        items.forEach { item ->
            NavigationBarItem(
                icon = { Icon(item.icon, contentDescription = item.label) },
                label = { Text(item.label) },
                selected = isSelected(currentRoute, item.route),
                onClick = dropUnlessResumed { onNavigate(item.route) }
            )
        }
    }
}

@Composable
fun ConnectNavigationRail(
    currentRoute: ConnectRoute,
    onNavigate: (ConnectRoute) -> Unit
) {
    NavigationRail {
        val items = listOf(
            NavigationItem("Dashboard", Icons.Rounded.Dashboard, Dashboard),
            NavigationItem("Terminal", Icons.Rounded.Terminal, Terminal()),
            NavigationItem("Repository", Icons.Rounded.Storage, Repository)
        )

        items.forEach { item ->
            NavigationRailItem(
                icon = { Icon(item.icon, contentDescription = item.label) },
                label = { Text(item.label) },
                selected = isSelected(currentRoute, item.route),
                onClick = dropUnlessResumed { onNavigate(item.route) }
            )
        }
    }
}

private data class NavigationItem(
    val label: String,
    val icon: ImageVector,
    val route: ConnectRoute
)

private fun isSelected(currentRoute: ConnectRoute, targetRoute: ConnectRoute): Boolean {
    return when (targetRoute) {
        is Dashboard -> currentRoute is Dashboard || currentRoute is DashboardDetail
        is Repository -> currentRoute is Repository || currentRoute is RepositoryDetail
        is Terminal -> currentRoute is Terminal
        else -> currentRoute == targetRoute
    }
}
