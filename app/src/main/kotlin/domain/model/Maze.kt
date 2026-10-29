package org.example.app.domain.model

data class Position(
    val row: Int,
    val col: Int,
)

// verticalWalls[r][c] == 1 это стена справа от клетки, horizontalWalls снизу.
// массивов на один больше чем клеток потому что последний столбец и последняя
// строка это внешняя граница. перепутаешь вертикальные с горизонтальными и всё
// поедет нахер
class Maze(
    val rows: Int,
    val cols: Int,
    val verticalWalls: Array<IntArray>,
    val horizontalWalls: Array<IntArray>,
) {
    // границы проверяем до того как лезть в массив, иначе вылетим за него
    fun canGo(
        from: Position,
        to: Position,
    ): Boolean {
        val dr = to.row - from.row
        val dc = to.col - from.col
        return when {
            dr == -1 && dc == 0 -> from.row > 0 && horizontalWalls[from.row - 1][from.col] == 0
            dr == 1 && dc == 0 -> from.row < rows - 1 && horizontalWalls[from.row][from.col] == 0
            dr == 0 && dc == -1 -> from.col > 0 && verticalWalls[from.row][from.col - 1] == 0
            dr == 0 && dc == 1 -> from.col < cols - 1 && verticalWalls[from.row][from.col] == 0
            else -> false
        }
    }

    fun openNeighbors(from: Position): List<Position> {
        val directions = listOf(-1 to 0, 1 to 0, 0 to -1, 0 to 1)
        return directions
            .map { (dr, dc) -> Position(from.row + dr, from.col + dc) }
            .filter { it.row in 0 until rows && it.col in 0 until cols && canGo(from, it) }
    }
}
