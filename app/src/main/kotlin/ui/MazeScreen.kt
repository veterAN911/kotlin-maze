package org.example.app.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.Button
import androidx.compose.material.RadioButton
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import org.example.app.domain.service.GameInterface
import org.example.app.ui.mapper.MazeUiMapper

// вкладка лабиринта, тут и генерация и файлы и решение. точки можно задать двумя
// способами, вписать числа в поля или ткнуть мышкой по клетке
@Composable
fun MazeScreen(
    game: GameInterface,
    mazeUiMapper: MazeUiMapper,
) {
    var maze by remember { mutableStateOf(game.generateMaze(10, 10)) }
    var solution by remember { mutableStateOf(emptyList<Position>()) }
    var start by remember { mutableStateOf<Position?>(null) }
    var end by remember { mutableStateOf<Position?>(null) }

    var rowsText by remember { mutableStateOf("10") }
    var colsText by remember { mutableStateOf("10") }

    // человек вводит точки от единицы как в примере тз (там было 10;1 и 6;10 на
    // поле 10 на 10), а модель у нас с нуля, разницу снимаем в pointFrom
    var startRowText by remember { mutableStateOf("1") }
    var startColText by remember { mutableStateOf("1") }
    var endRowText by remember { mutableStateOf("10") }
    var endColText by remember { mutableStateOf("10") }

    var error by remember { mutableStateOf<String?>(null) }

    // что поставит следующий клик по полю, старт или финиш
    var clickStart by remember { mutableStateOf(true) }

    // из полей ввода делаем точку. если там пока не число или оно вне лабиринта
    // то null и метку просто не показываем
    fun pointFrom(
        rowText: String,
        colText: String,
    ): Position? {
        val row = rowText.toIntOrNull() ?: return null
        val col = colText.toIntOrNull() ?: return null
        if (!inMaze(maze, row, col)) return null
        return Position(row - 1, col - 1)
    }

    fun showMaze(newMaze: Maze) {
        maze = newMaze
        solution = emptyList()
        rowsText = newMaze.rows.toString()
        colsText = newMaze.cols.toString()
        startRowText = "1"
        startColText = "1"
        endRowText = newMaze.rows.toString()
        endColText = newMaze.cols.toString()
        start = Position(0, 0)
        end = Position(newMaze.rows - 1, newMaze.cols - 1)
        error = null
    }

    // клик по полю ставит выбранную точку и заодно переписывает поля ввода, чтобы
    // оба способа показывали одно и то же. старый маршрут убираем, он посчитан
    // для прежних точек
    fun clickCell(
        row: Int,
        col: Int,
    ) {
        if (clickStart) {
            startRowText = (row + 1).toString()
            startColText = (col + 1).toString()
            start = Position(row, col)
        } else {
            endRowText = (row + 1).toString()
            endColText = (col + 1).toString()
            end = Position(row, col)
        }
        solution = emptyList()
        error = null
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

    val load: () -> Unit = {
        val path = chooseFile("Загрузить лабиринт", save = false)
        if (path != null) {
            try {
                showMaze(game.loadMaze(path))
            } catch (e: Exception) {
                error = "Не удалось загрузить файл: ${e.message}"
            }
        }
    }

    val save: () -> Unit = {
        val path = chooseFile("Сохранить лабиринт", save = true)
        if (path != null) {
            try {
                game.saveMaze(maze, path)
                error = null
            } catch (e: Exception) {
                error = "Не удалось сохранить файл: ${e.message}"
            }
        }
    }

    // кнопка работает туда-сюда, показать маршрут или убрать его
    val solve: () -> Unit = {
        if (solution.isNotEmpty()) {
            solution = emptyList()
            start = null
            end = null
            error = null
        } else {
            val startRow = startRowText.toIntOrNull()
            val startCol = startColText.toIntOrNull()
            val endRow = endRowText.toIntOrNull()
            val endCol = endColText.toIntOrNull()

            if (startRow == null || startCol == null || endRow == null || endCol == null) {
                error = "Координаты точек — целые числа"
            } else if (!inMaze(maze, startRow, startCol)) {
                error = "Старт вне лабиринта: строка 1..${maze.rows}, столбец 1..${maze.cols}"
            } else if (!inMaze(maze, endRow, endCol)) {
                error = "Финиш вне лабиринта: строка 1..${maze.rows}, столбец 1..${maze.cols}"
            } else {
                // вот тут и снимаем ту самую единицу, в модели всё с нуля
                val from = Position(startRow - 1, startCol - 1)
                val to = Position(endRow - 1, endCol - 1)
                val path = game.solveMaze(maze, from, to)
                solution = path
                start = from
                end = to
                error = if (path.isEmpty()) "Путь не найден" else null
            }
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
            Button(onClick = generate) { Text("Сгенерировать") }
            Button(onClick = load) { Text("Загрузить") }
            Button(onClick = save) { Text("Сохранить") }
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text("Старт:")
            NumberField("строка", startRowText) {
                startRowText = it
                start = pointFrom(it, startColText)
            }
            NumberField("столбец", startColText) {
                startColText = it
                start = pointFrom(startRowText, it)
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text("Финиш:")
            NumberField("строка", endRowText) {
                endRowText = it
                end = pointFrom(it, endColText)
            }
            NumberField("столбец", endColText) {
                endColText = it
                end = pointFrom(endRowText, it)
            }
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text("Клик по полю ставит:")
            RadioButton(selected = clickStart, onClick = { clickStart = true })
            Text("старт")
            RadioButton(selected = !clickStart, onClick = { clickStart = false })
            Text("финиш")
        }

        Button(onClick = solve) {
            Text(if (solution.isNotEmpty()) "Убрать решение" else "Показать решение")
        }

        error?.let { Text(it, color = Color(0xFFD32F2F)) }

        MazeCanvas(
            maze = maze,
            solution = solution,
            start = start,
            end = end,
            mazeUiMapper = mazeUiMapper,
            onCellClick = { row, col -> clickCell(row, col) },
        )
    }
}
