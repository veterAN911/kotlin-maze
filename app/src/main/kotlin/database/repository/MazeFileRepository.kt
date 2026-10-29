package org.example.app.database.repository

import org.example.app.database.mapper.MazeMapper
import org.example.app.database.model.MazeFileModel
import org.example.app.domain.model.Maze
import java.io.File

// формат из тз такой: первая строка "rows cols", дальше матрица вертикальных стен
// rows строк по cols чисел, пустая строка, потом матрица горизонтальных стен.
// пустую строку просто выкидываем фильтром так что файл и без неё прочитается
class MazeFileRepository(
    private val mapper: MazeMapper,
) : MazeRepository {
    override fun load(path: String): Maze = parse(File(path).readText())

    override fun parse(text: String): Maze {
        val lines = text.lines().filter { it.isNotBlank() }
        require(lines.size >= 3) { "Файл пуст или имеет неверный формат" }

        // в первой строке размеры, режем по любым пробелам чтобы не зависеть от
        // того одним пробелом там разделено или табом
        val size = lines[0].trim().split(Regex("\\s+")).filter { it.isNotBlank() }
        require(size.size == 2) { "Первая строка должна содержать число строк и столбцов" }
        val rows = size[0].toIntOrNull() ?: throw IllegalArgumentException("Число строк должно быть целым числом")
        val cols = size[1].toIntOrNull() ?: throw IllegalArgumentException("Число столбцов должно быть целым числом")
        require(rows in 1..50 && cols in 1..50) { "Размеры лабиринта должны быть от 1 до 50" }

        // число строк проверяем ДО subList, иначе на обрезанном файле subList тихо
        // отдаст ерунду вместо ошибки
        require(lines.size == 1 + rows * 2) { "Число строк в файле не соответствует размеру лабиринта" }
        val vertical = lines.subList(1, 1 + rows).map { parseRow(it, cols) }
        val horizontal = lines.subList(1 + rows, 1 + rows * 2).map { parseRow(it, cols) }

        return mapper.toDomain(MazeFileModel(rows, cols, vertical, horizontal))
    }

    override fun save(
        maze: Maze,
        path: String,
    ) = File(path).writeText(toText(maze))

    override fun toText(maze: Maze): String =
        buildString {
            append("${maze.rows} ${maze.cols}\n")
            maze.verticalWalls.forEach { appendRow(it) }
            append("\n")
            maze.horizontalWalls.forEach { appendRow(it) }
        }

    private fun StringBuilder.appendRow(row: IntArray) {
        append(row.joinToString(" "))
        append("\n")
    }

    private fun parseRow(
        line: String,
        cols: Int,
    ): List<Int> {
        val values = line.trim().split(Regex("\\s+")).filter { it.isNotBlank() }
        require(values.size == cols) { "Неверное число столбцов в матрице стен" }
        val ints =
            values.map {
                it.toIntOrNull() ?: throw IllegalArgumentException("В матрице стен есть нечисловое значение")
            }
        // всякие 2 и -1 потом ломают canGo, лучше отловить тут чем искать потом
        // откуда лабиринт поехал
        require(ints.all { it == 0 || it == 1 }) { "Значения стен должны быть 0 или 1" }
        return ints
    }
}
