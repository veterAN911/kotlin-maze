package org.example.app

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Tab
import androidx.compose.material.TabRow
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.WindowState
import androidx.compose.ui.window.application
import org.example.app.di.AppContainer
import org.example.app.ui.AgentScreen
import org.example.app.ui.CaveScreen
import org.example.app.ui.MazeScreen

fun desktopApp() =
    application {
        Window(
            onCloseRequest = ::exitApplication,
            title = "Maze",
            state = WindowState(width = 640.dp, height = 840.dp),
        ) {
            MaterialTheme {
                AppTabs()
            }
        }
    }

@Composable
private fun AppTabs() {
    var tab by remember { mutableStateOf(0) }
    val titles = listOf("Лабиринт", "Пещера", "Агент")

    Column(modifier = Modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = tab) {
            titles.forEachIndexed { index, title ->
                Tab(
                    selected = tab == index,
                    onClick = { tab = index },
                    text = { Text(title) },
                )
            }
        }

        // номера вкладок идут по порядку titles, добавляешь вкладку -- не забудь
        // поправить и тут
        when (tab) {
            0 -> MazeScreen(game = AppContainer.game, mazeUiMapper = AppContainer.mazeUiMapper)
            1 -> CaveScreen(game = AppContainer.game)
            else -> AgentScreen(game = AppContainer.game, mazeUiMapper = AppContainer.mazeUiMapper)
        }
    }
}
