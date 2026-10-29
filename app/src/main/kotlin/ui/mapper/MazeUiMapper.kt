package org.example.app.ui.mapper

import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position

data class UiPoint(
    val x: Float,
    val y: Float,
)

data class UiLine(
    val x1: Float,
    val y1: Float,
    val x2: Float,
    val y2: Float,
)

// считаем не в пикселях а в клетках, клетка это единица. в пиксели переводит уже
// MazeCanvas, поэтому окно можно тянуть как угодно и ничего не поедет
class MazeUiMapper {
    // верхнюю и левую границу дорисовываем руками, в матрицах лежат только правая
    // и нижняя стенки клетки. забудешь их и лабиринт будет без двух стенок
    fun wallLines(maze: Maze): List<UiLine> {
        val lines = mutableListOf<UiLine>()
        val rows = maze.rows.toFloat()
        val cols = maze.cols.toFloat()

        lines += UiLine(0f, 0f, cols, 0f)
        lines += UiLine(0f, 0f, 0f, rows)

        for (r in 0 until maze.rows) {
            for (c in 0 until maze.cols) {
                if (maze.verticalWalls[r][c] == 1) {
                    lines += UiLine(c + 1f, r.toFloat(), c + 1f, r + 1f)
                }
                if (maze.horizontalWalls[r][c] == 1) {
                    lines += UiLine(c.toFloat(), r + 1f, c + 1f, r + 1f)
                }
            }
        }
        return lines
    }

    // плюс полклетки чтобы линия шла через центр, а не по углу
    fun pathPoints(path: List<Position>): List<UiPoint> = path.map { UiPoint(it.col + 0.5f, it.row + 0.5f) }
}
