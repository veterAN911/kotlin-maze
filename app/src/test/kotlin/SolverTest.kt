package org.example.app

import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.algorithm.MazeSolver
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class SolverTest {
    @Test
    fun `solves a known 2x2 maze`() {
        val maze =
            Maze(
                rows = 2,
                cols = 2,
                verticalWalls = arrayOf(intArrayOf(0, 1), intArrayOf(0, 1)),
                horizontalWalls = arrayOf(intArrayOf(1, 0), intArrayOf(1, 1)),
            )
        val path = MazeSolver().solve(maze, Position(0, 0), Position(1, 0))
        assertEquals(listOf(Position(0, 0), Position(0, 1), Position(1, 1), Position(1, 0)), path)
    }

    @Test
    fun `from a middle cell picks the shortest of two routes`() {
        // от (0,0) до (2,2) тут два маршрута, на 7 клеток и на 9. должен взять
        // короткий, иначе bfs сделан неправильно
        val maze =
            Maze(
                rows = 3,
                cols = 3,
                verticalWalls =
                    arrayOf(
                        intArrayOf(0, 0, 1),
                        intArrayOf(0, 0, 1),
                        intArrayOf(0, 0, 1),
                    ),
                horizontalWalls =
                    arrayOf(
                        intArrayOf(1, 1, 0),
                        intArrayOf(0, 0, 1),
                        intArrayOf(1, 1, 1),
                    ),
            )
        val path = MazeSolver().solve(maze, Position(0, 0), Position(2, 2))
        assertEquals(
            listOf(
                Position(0, 0),
                Position(0, 1),
                Position(0, 2),
                Position(1, 2),
                Position(1, 1),
                Position(2, 1),
                Position(2, 2),
            ),
            path,
        )
    }

    @Test
    fun `start equals end returns single cell`() {
        val maze = EllerMazeGenerator().generate(5, 5, Random(1))
        assertEquals(listOf(Position(2, 2)), MazeSolver().solve(maze, Position(2, 2), Position(2, 2)))
    }

    @Test
    fun `solves any generated maze from corner to corner`() {
        for (rows in 1..10) {
            for (cols in 1..10) {
                val maze = EllerMazeGenerator().generate(rows, cols, Random(7))
                val start = Position(0, 0)
                val end = Position(rows - 1, cols - 1)
                val path = MazeSolver().solve(maze, start, end)
                assertTrue(path.isNotEmpty(), "no path in $rows x $cols maze")
                assertEquals(start, path.first())
                assertEquals(end, path.last())
                assertTrue(isValidPath(maze, path), "path is invalid in $rows x $cols maze")
            }
        }
    }

    @Test
    fun `out of bounds returns empty path`() {
        val maze = EllerMazeGenerator().generate(5, 5)
        assertEquals(emptyList(), MazeSolver().solve(maze, Position(-1, 0), Position(4, 4)))
        assertEquals(emptyList(), MazeSolver().solve(maze, Position(5, 0), Position(4, 4)))
        assertEquals(emptyList(), MazeSolver().solve(maze, Position(0, -1), Position(4, 4)))
        assertEquals(emptyList(), MazeSolver().solve(maze, Position(0, 5), Position(4, 4)))
        assertEquals(emptyList(), MazeSolver().solve(maze, Position(0, 0), Position(5, 4)))
    }

    @Test
    fun `no path returns empty list`() {
        // лабиринт из одних стен, каждая клетка сама по себе
        val maze =
            Maze(
                rows = 2,
                cols = 2,
                verticalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
                horizontalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
            )
        assertEquals(emptyList(), MazeSolver().solve(maze, Position(0, 0), Position(1, 1)))
    }

    private fun isValidPath(
        maze: Maze,
        path: List<Position>,
    ): Boolean {
        for (i in 0 until path.size - 1) {
            if (!maze.canGo(path[i], path[i + 1])) return false
        }
        return true
    }
}
