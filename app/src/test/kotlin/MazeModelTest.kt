package org.example.app

import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class MazeModelTest {
    // лабиринт 2x2, если нарисовать то вот так, проходы (0,0)-(0,1), (0,1)-(1,1)
    // и (1,1)-(1,0):
    //   (0,0) - (0,1)
    //           |
    //   (1,0) - (1,1)
    // по массивам стен это глазами не читается, так что пусть будет
    private val maze =
        Maze(
            rows = 2,
            cols = 2,
            verticalWalls = arrayOf(intArrayOf(0, 1), intArrayOf(0, 1)),
            horizontalWalls = arrayOf(intArrayOf(1, 0), intArrayOf(1, 1)),
        )

    @Test
    fun `an open passage lets the step through`() {
        assertTrue(maze.canGo(Position(0, 0), Position(0, 1)))
        assertTrue(maze.canGo(Position(0, 1), Position(1, 1)))
        assertTrue(maze.canGo(Position(1, 1), Position(1, 0)))
    }

    @Test
    fun `a wall blocks the step`() {
        assertFalse(maze.canGo(Position(0, 0), Position(1, 0)), "стена снизу должна мешать")
    }

    @Test
    fun `the outer border does not let the step out`() {
        val rows = 3
        val cols = 3
        val open =
            Maze(
                rows = rows,
                cols = cols,
                verticalWalls = Array(rows) { IntArray(cols) },
                horizontalWalls = Array(rows) { IntArray(cols) },
            )

        assertFalse(open.canGo(Position(0, 0), Position(-1, 0)), "выход вверх за поле")
        assertFalse(open.canGo(Position(rows - 1, 0), Position(rows, 0)), "выход вниз за поле")
        assertFalse(open.canGo(Position(0, 0), Position(0, -1)), "выход влево за поле")
        assertFalse(open.canGo(Position(0, cols - 1), Position(0, cols)), "выход вправо за поле")
    }

    @Test
    fun `a step through the side is forbidden`() {
        assertFalse(maze.canGo(Position(0, 0), Position(1, 1)), "по диагонали ходить нельзя")
        assertFalse(maze.canGo(Position(0, 0), Position(0, 0)), "шаг на месте — не шаг")
    }

    @Test
    fun `open neighbours of a corner are its passages`() {
        assertEquals(listOf(Position(0, 1)), maze.openNeighbors(Position(0, 0)))
        assertEquals(listOf(Position(0, 1), Position(1, 0)), maze.openNeighbors(Position(1, 1)))
    }

    @Test
    fun `a cell in the middle of an open maze has four neighbours`() {
        val size = 3
        val open =
            Maze(
                rows = size,
                cols = size,
                verticalWalls = Array(size) { IntArray(size) },
                horizontalWalls = Array(size) { IntArray(size) },
            )

        assertEquals(4, open.openNeighbors(Position(1, 1)).size)
        assertEquals(2, open.openNeighbors(Position(0, 0)).size)
    }

    @Test
    fun `a walled off cell has no neighbours`() {
        val walled =
            Maze(
                rows = 2,
                cols = 2,
                verticalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
                horizontalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
            )

        assertEquals(emptyList(), walled.openNeighbors(Position(0, 0)))
    }
}
