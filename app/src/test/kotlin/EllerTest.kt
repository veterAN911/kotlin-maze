package org.example.app

import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class EllerTest {
    @Test
    fun `generated maze is perfect for sizes from 1x1 to 10x10`() {
        for (rows in 1..10) {
            for (cols in 1..10) {
                val maze = EllerMazeGenerator().generate(rows, cols, Random(42))
                assertTrue(maze.rows == rows && maze.cols == cols)
                assertTrue(isPerfect(maze), "Maze $rows x $cols is not perfect")
            }
        }
    }

    @Test
    fun `size must not exceed 50`() {
        assertFailsWith<IllegalArgumentException> {
            EllerMazeGenerator().generate(51, 10)
        }
        assertFailsWith<IllegalArgumentException> {
            EllerMazeGenerator().generate(10, 51)
        }
        assertFailsWith<IllegalArgumentException> {
            EllerMazeGenerator().generate(0, 10)
        }
        assertFailsWith<IllegalArgumentException> {
            EllerMazeGenerator().generate(10, 0)
        }
    }

    // идеальный значит проходов ровно rows*cols - 1 и все клетки достижимы
    private fun isPerfect(maze: Maze): Boolean = openPassages(maze) == maze.rows * maze.cols - 1 && allReachable(maze)

    private fun openPassages(maze: Maze): Int {
        var open = 0
        for (r in 0 until maze.rows) {
            for (c in 0 until maze.cols) {
                if (c < maze.cols - 1 && maze.verticalWalls[r][c] == 0) open++
                if (r < maze.rows - 1 && maze.horizontalWalls[r][c] == 0) open++
            }
        }
        return open
    }

    private fun allReachable(maze: Maze): Boolean {
        val visited = Array(maze.rows) { BooleanArray(maze.cols) }
        val queue = ArrayDeque<Position>()
        visited[0][0] = true
        queue.add(Position(0, 0))
        var count = 0
        while (queue.isNotEmpty()) {
            val current = queue.removeFirst()
            count++
            for (next in maze.openNeighbors(current)) {
                if (!visited[next.row][next.col]) {
                    visited[next.row][next.col] = true
                    queue.add(next)
                }
            }
        }
        return count == maze.rows * maze.cols
    }
}
