package org.example.app.domain.model

// 1 это живая клетка то есть стена, 0 мёртвая то есть свободно. в файле пещеры
// лежат те же нолики с единичками так что ничего не преобразовываем
class Cave(
    val rows: Int,
    val cols: Int,
    val cells: Array<IntArray>,
) {
    fun isAlive(
        row: Int,
        col: Int,
    ): Boolean = cells[row][col] == 1

    // самое мутное место в пещере, тут за границей поля сосед считается ЖИВЫМ (в
    // тз так). поэтому у углов поля соседей как бы пять, у края три, из за этого
    // пещера сама себя затягивает стенками по краям. поменяешь единичку на нолик
    // и форма пещер станет совсем другая
    fun aliveNeighbours(
        row: Int,
        col: Int,
    ): Int {
        var count = 0
        for (dRow in -1..1) {
            for (dCol in -1..1) {
                if (dRow == 0 && dCol == 0) continue
                val r = row + dRow
                val c = col + dCol
                count += if (r in 0 until rows && c in 0 until cols) cells[r][c] else 1
            }
        }
        return count
    }

    fun isSameAs(other: Cave): Boolean =
        rows == other.rows &&
            cols == other.cols &&
            cells.indices.all { cells[it].contentEquals(other.cells[it]) }
}
