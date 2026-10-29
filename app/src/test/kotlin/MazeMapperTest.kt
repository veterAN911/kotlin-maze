package org.example.app

import org.example.app.database.mapper.MazeMapper
import org.example.app.database.model.MazeFileModel
import org.example.app.domain.model.Maze
import kotlin.test.Test
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class MazeMapperTest {
    @Test
    fun `domain to file and back keeps data`() {
        val maze =
            Maze(
                rows = 2,
                cols = 2,
                verticalWalls = arrayOf(intArrayOf(0, 1), intArrayOf(0, 1)),
                horizontalWalls = arrayOf(intArrayOf(1, 0), intArrayOf(1, 1)),
            )
        val restored = MazeMapper().toDomain(MazeMapper().toFile(maze))
        assertTrue(maze.rows == restored.rows && maze.cols == restored.cols)
        assertTrue(maze.verticalWalls.contentDeepEquals(restored.verticalWalls))
        assertTrue(maze.horizontalWalls.contentDeepEquals(restored.horizontalWalls))
    }

    @Test
    fun `rejects wrong wall values`() {
        val file =
            MazeFileModel(
                rows = 2,
                cols = 2,
                verticalWalls = listOf(listOf(0, 1), listOf(2, 1)),
                horizontalWalls = listOf(listOf(0, 0), listOf(1, 1)),
            )
        assertFailsWith<IllegalArgumentException> { MazeMapper().toDomain(file) }
    }

    @Test
    fun `rejects size over 50`() {
        val file =
            MazeFileModel(
                rows = 51,
                cols = 10,
                verticalWalls = List(51) { List(10) { 0 } },
                horizontalWalls = List(51) { List(10) { 0 } },
            )
        assertFailsWith<IllegalArgumentException> { MazeMapper().toDomain(file) }
    }
}
