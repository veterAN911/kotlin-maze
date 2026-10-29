package org.example.app.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.example.app.domain.algorithm.QLearningAgent
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import org.example.app.domain.service.GameInterface
import org.example.app.ui.mapper.MazeUiMapper

// вкладка агента. порядок как в тз: грузим лабиринт, задаём финиш, обучаем, а
// потом спрашиваем маршрут из любой точки. лабиринт и финиш после обучения
// трогать нельзя
//
// клик по полю работает в два этапа: пока агент не обучен он ставит финиш, а
// после обучения старт, потому что финиш уже закреплён
@Composable
fun AgentScreen(
    game: GameInterface,
    mazeUiMapper: MazeUiMapper,
) {
    var maze by remember { mutableStateOf<Maze?>(null) }
    var agent by remember { mutableStateOf<QLearningAgent?>(null) }

    var path by remember { mutableStateOf(emptyList<Position>()) }
    var start by remember { mutableStateOf<Position?>(null) }
    var end by remember { mutableStateOf<Position?>(null) }

    var rowsText by remember { mutableStateOf("10") }
    var colsText by remember { mutableStateOf("10") }
    var endRowText by remember { mutableStateOf("10") }
    var endColText by remember { mutableStateOf("10") }
    var startRowText by remember { mutableStateOf("1") }
    var startColText by remember { mutableStateOf("1") }

    var training by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    // из полей ввода делаем точку, если там пока не число или оно вне лабиринта
    // то null и метку просто не показываем
    fun pointFrom(
        rowText: String,
        colText: String,
    ): Position? {
        val current = maze ?: return null
        val row = rowText.toIntOrNull() ?: return null
        val col = colText.toIntOrNull() ?: return null
        if (!inMaze(current, row, col)) return null
        return Position(row - 1, col - 1)
    }

    // новый лабиринт, значит старый агент обучен не на нём и его надо забыть
    fun showMaze(newMaze: Maze) {
        maze = newMaze
        agent = null
        path = emptyList()
        rowsText = newMaze.rows.toString()
        colsText = newMaze.cols.toString()
        endRowText = newMaze.rows.toString()
        endColText = newMaze.cols.toString()
        startRowText = "1"
        startColText = "1"
        start = null
        end = Position(newMaze.rows - 1, newMaze.cols - 1)
        error = null
    }

    // клик по полю. пока агент не обучен ставим финиш, после обучения старт,
    // финиш к тому моменту уже закреплён и менять его нельзя
    fun clickCell(
        row: Int,
        col: Int,
    ) {
        if (agent == null) {
            endRowText = (row + 1).toString()
            endColText = (col + 1).toString()
            end = Position(row, col)
        } else {
            startRowText = (row + 1).toString()
            startColText = (col + 1).toString()
            start = Position(row, col)
            path = emptyList()
        }
        error = null
    }

    val load: () -> Unit = {
        val selected = chooseFile("Загрузить лабиринт для агента", save = false)
        if (selected != null) {
            try {
                showMaze(game.loadMaze(selected))
            } catch (e: Exception) {
                error = "Не удалось загрузить файл: ${e.message}"
            }
        }
    }

    val generate: () -> Unit = {
        val rows = rowsText.toIntOrNull()
        val cols = colsText.toIntOrNull()
        if (rows == null || cols == null || rows !in 1..50 || cols !in 1..50) {
            error = "Размеры лабиринта — числа от 1 до 50"
        } else {
            showMaze(game.generateMaze(rows, cols))
        }
    }

    // обучение на большом лабиринте идёт секунды, поэтому уводим его в отдельный
    // поток, иначе окно замёрзнет и человек подумает что всё повисло
    val train: () -> Unit = {
        val current = maze
        val endRow = endRowText.toIntOrNull()
        val endCol = endColText.toIntOrNull()

        if (current == null) {
            error = "Сначала загрузите лабиринт"
        } else if (endRow == null || endCol == null) {
            error = "Координаты финиша — целые числа"
        } else if (!inMaze(current, endRow, endCol)) {
            error = "Финиш вне лабиринта: строка 1..${current.rows}, столбец 1..${current.cols}"
        } else {
            val finish = Position(endRow - 1, endCol - 1)
            training = true
            error = null
            path = emptyList()
            start = null
            end = finish
            scope.launch {
                agent = withContext(Dispatchers.Default) { game.trainAgent(current, finish) }
                training = false
            }
        }
    }

    val showPath: () -> Unit = {
        val current = maze
        val trained = agent
        val startRow = startRowText.toIntOrNull()
        val startCol = startColText.toIntOrNull()

        if (current == null || trained == null) {
            error = "Сначала обучите агента"
        } else if (startRow == null || startCol == null) {
            error = "Координаты старта — целые числа"
        } else if (!inMaze(current, startRow, startCol)) {
            error = "Старт вне лабиринта: строка 1..${current.rows}, столбец 1..${current.cols}"
        } else {
            val from = Position(startRow - 1, startCol - 1)
            val route = game.agentPath(trained, from)
            path = route
            start = from
            error = if (route.isEmpty()) "Агент не знает выхода из этой клетки" else null
        }
    }

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            NumberField("Строки:", rowsText) { rowsText = it }
            NumberField("Колонки:", colsText) { colsText = it }
            Button(onClick = generate, enabled = !training) { Text("Сгенерировать") }
            Button(onClick = load, enabled = !training) { Text("Загрузить файл") }
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text("Финиш:")
            NumberField("строка", endRowText) {
                endRowText = it
                // после обучения финиш закреплён, двигать его нельзя
                if (agent == null) end = pointFrom(it, endColText)
            }
            NumberField("столбец", endColText) {
                endColText = it
                if (agent == null) end = pointFrom(endRowText, it)
            }
            Button(onClick = train, enabled = !training && maze != null) { Text("Обучить агента") }
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text("Старт:")
            NumberField("строка", startRowText) {
                startRowText = it
                if (agent != null) start = pointFrom(it, startColText)
            }
            NumberField("столбец", startColText) {
                startColText = it
                if (agent != null) start = pointFrom(startRowText, it)
            }
            Button(onClick = showPath, enabled = !training && agent != null) { Text("Показать маршрут") }
        }

        // кнопки во время обучения выключены, поэтому тут просто пишем что ждём
        if (training) {
            Text("Идёт обучение, подождите…")
        } else if (agent != null) {
            Text("Обучение закончено: ${agent!!.episodesDone} проходов. Клик по полю ставит старт")
        } else if (maze == null) {
            Text("Загрузите файл лабиринта или сгенерируйте новый")
        } else {
            Text("Клик по полю ставит финиш")
        }

        error?.let { Text(it, color = Color(0xFFD32F2F)) }

        MazeCanvas(
            maze = maze,
            solution = path,
            start = start,
            end = end,
            mazeUiMapper = mazeUiMapper,
            onCellClick = { row, col -> clickCell(row, col) },
        )
    }
}
