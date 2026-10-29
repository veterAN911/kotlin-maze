package org.example.app.database.mapper

import org.example.app.database.model.MazeFileModel
import org.example.app.domain.model.Maze

// перекладываем из файловой модели в доменную и обратно
class MazeMapper {
    fun toDomain(file: MazeFileModel): Maze {
        require(file.rows in 1..50 && file.cols in 1..50) { "Размеры лабиринта должны быть от 1 до 50" }
        require(file.verticalWalls.size == file.rows && file.horizontalWalls.size == file.rows) {
            "Неверное число строк в матрицах стен"
        }
        val vertical = file.verticalWalls.map { parseRow(it, file.cols) }.toTypedArray()
        val horizontal = file.horizontalWalls.map { parseRow(it, file.cols) }.toTypedArray()

        // в матрицах лежат только правая и нижняя стенки клетки, а внешняя граница
        // должна быть сплошной. дырявая граница ломает переходы, поэтому проверяем
        require(vertical.all { it[file.cols - 1] == 1 }) { "Правая граница лабиринта должна быть сплошной (1)" }
        require(horizontal[file.rows - 1].all { it == 1 }) { "Нижняя граница лабиринта должна быть сплошной (1)" }
        return Maze(file.rows, file.cols, vertical, horizontal)
    }

    fun toFile(maze: Maze): MazeFileModel =
        MazeFileModel(
            rows = maze.rows,
            cols = maze.cols,
            verticalWalls = maze.verticalWalls.map { it.toList() },
            horizontalWalls = maze.horizontalWalls.map { it.toList() },
        )

    private fun parseRow(
        row: List<Int>,
        cols: Int,
    ): IntArray {
        require(row.size == cols) { "Неверное число столбцов в матрице стен" }
        require(row.all { it == 0 || it == 1 }) { "Значения стен должны быть 0 или 1" }
        return row.toIntArray()
    }
}
