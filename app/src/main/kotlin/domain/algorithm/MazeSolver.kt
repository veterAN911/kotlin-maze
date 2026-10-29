package org.example.app.domain.algorithm

import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position

// обход в ширину, поэтому до финиша дойдём самым коротким путём из всех. путь
// собираем обратно по предкам
class MazeSolver {
    fun solve(
        maze: Maze,
        start: Position,
        end: Position,
    ): List<Position> {
        if (!inBounds(maze, start) || !inBounds(maze, end)) return emptyList()
        if (start == end) return listOf(start)

        val visited = Array(maze.rows) { BooleanArray(maze.cols) }
        val previous = Array(maze.rows) { arrayOfNulls<Position>(maze.cols) }
        val queue = ArrayDeque<Position>()

        visited[start.row][start.col] = true
        queue.add(start)

        while (queue.isNotEmpty()) {
            val current = queue.removeFirst()
            for (next in maze.openNeighbors(current)) {
                if (visited[next.row][next.col]) continue
                visited[next.row][next.col] = true
                previous[next.row][next.col] = current
                if (next == end) return buildPath(previous, end)
                queue.add(next)
            }
        }
        return emptyList()
    }

    private fun inBounds(
        maze: Maze,
        position: Position,
    ): Boolean = position.row in 0 until maze.rows && position.col in 0 until maze.cols

    // идём от финиша назад по предкам, у старта предка нет поэтому там null и цикл
    // сам останавливается. набрали задом наперёд, поэтому разворачиваем
    private fun buildPath(
        previous: Array<Array<Position?>>,
        end: Position,
    ): List<Position> {
        val path = mutableListOf<Position>()
        var current: Position? = end
        while (current != null) {
            path.add(current)
            current = previous[current.row][current.col]
        }
        return path.asReversed()
    }
}
