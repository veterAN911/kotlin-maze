package org.example.app.database.repository

import org.example.app.domain.model.Cave
import java.io.File

// формат пещеры проще чем у лабиринта, второй матрицы и пустой строки тут нет:
// первая строка "rows cols", дальше rows строк по cols чисел
class CaveFileRepository : CaveRepository {
    override fun load(path: String): Cave {
        val lines = File(path).readLines().filter { it.isNotBlank() }
        require(lines.size >= 2) { "Файл пуст или имеет неверный формат" }

        val size = lines[0].trim().split(Regex("\\s+")).filter { it.isNotBlank() }
        require(size.size == 2) { "Первая строка должна содержать число строк и столбцов" }
        val rows = size[0].toIntOrNull() ?: throw IllegalArgumentException("Число строк должно быть целым числом")
        val cols = size[1].toIntOrNull() ?: throw IllegalArgumentException("Число столбцов должно быть целым числом")
        require(rows in 1..50 && cols in 1..50) { "Размеры пещеры должны быть от 1 до 50" }

        // число строк проверяем заранее, иначе subList на обрезанном файле вернёт
        // что попало и получим пещеру не того размера вместо понятной ошибки
        require(lines.size == 1 + rows) { "Число строк в файле не соответствует размеру пещеры" }
        val cells = lines.subList(1, 1 + rows).map { parseRow(it, cols) }.toTypedArray()

        return Cave(rows, cols, cells)
    }

    override fun save(
        cave: Cave,
        path: String,
    ) {
        val text =
            buildString {
                append("${cave.rows} ${cave.cols}\n")
                cave.cells.forEach {
                    append(it.joinToString(" "))
                    append("\n")
                }
            }
        File(path).writeText(text)
    }

    private fun parseRow(
        line: String,
        cols: Int,
    ): IntArray {
        val values = line.trim().split(Regex("\\s+")).filter { it.isNotBlank() }
        require(values.size == cols) { "Неверное число столбцов в матрице пещеры" }

        val cells =
            values.map {
                it.toIntOrNull() ?: throw IllegalArgumentException("В матрице пещеры есть нечисловое значение")
            }
        require(cells.all { it == 0 || it == 1 }) { "Значения клеток должны быть 0 или 1" }
        return cells.toIntArray()
    }
}
