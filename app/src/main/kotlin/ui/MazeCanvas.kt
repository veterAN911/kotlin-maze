package org.example.app.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import org.example.app.ui.mapper.MazeUiMapper

// тз говорит поле 500 на 500 и стена 2 пикселя
val FIELD_SIZE = 500.dp
private const val WALL_WIDTH = 2f

// маршрут обязан отличаться от стен и поля (тз), поэтому красный а не серый
private val WALL_COLOR = Color(0xFF2E2E2E)
private val FIELD_COLOR = Color.White
private val PATH_COLOR = Color(0xFFE53935)
private val START_COLOR = Color(0xFF2E7D32)
private val END_COLOR = Color(0xFF1565C0)

// одна рисовалка на все экраны, иначе пришлось бы держать две копии и они бы
// разъехались. последний параметр это клик по полю, если он не нужен то можно
// не передавать
@Composable
fun MazeCanvas(
    maze: Maze?,
    solution: List<Position>,
    start: Position?,
    end: Position?,
    mazeUiMapper: MazeUiMapper,
    onCellClick: ((Int, Int) -> Unit)? = null,
) {
    Canvas(
        modifier =
            Modifier
                .size(FIELD_SIZE)
                .background(FIELD_COLOR)
                .pointerInput(maze, onCellClick) {
                    if (maze == null || onCellClick == null) return@pointerInput
                    detectTapGestures { point ->
                        // из пикселей в клетку. делим на размер клетки и прижимаем к
                        // краям, иначе по самому краю поля можно получить лишнюю клетку
                        val cellW = size.width / maze.cols
                        val cellH = size.height / maze.rows
                        val col = (point.x / cellW).toInt().coerceIn(0, maze.cols - 1)
                        val row = (point.y / cellH).toInt().coerceIn(0, maze.rows - 1)
                        onCellClick(row, col)
                    }
                },
    ) {
        if (maze == null) return@Canvas

        // высоту считаем отдельно от ширины, лабиринт может быть не квадратный
        val cellW = size.width / maze.cols
        val cellH = size.height / maze.rows

        // двойку в пикселях брать нельзя, на экране с большой плотностью стена
        // станет волосинкой. тянем пропорционально полю чтобы два пикселя на 500
        // сохранялись
        val wallWidth = size.width * WALL_WIDTH / FIELD_SIZE.value

        for (line in mazeUiMapper.wallLines(maze)) {
            drawLine(
                color = WALL_COLOR,
                start = Offset(line.x1 * cellW, line.y1 * cellH),
                end = Offset(line.x2 * cellW, line.y2 * cellH),
                strokeWidth = wallWidth,
            )
        }

        val points = mazeUiMapper.pathPoints(solution)
        for (i in 0 until points.size - 1) {
            drawLine(
                color = PATH_COLOR,
                start = Offset(points[i].x * cellW, points[i].y * cellH),
                end = Offset(points[i + 1].x * cellW, points[i + 1].y * cellH),
                strokeWidth = wallWidth,
            )
        }

        // радиус кружка берём от клетки чтобы на любом размере смотрелось одинаково
        start?.let {
            drawCircle(
                color = START_COLOR,
                radius = cellW * 0.18f,
                center = Offset((it.col + 0.5f) * cellW, (it.row + 0.5f) * cellH),
            )
        }
        end?.let {
            drawCircle(
                color = END_COLOR,
                radius = cellW * 0.18f,
                center = Offset((it.col + 0.5f) * cellW, (it.row + 0.5f) * cellH),
            )
        }
    }
}
