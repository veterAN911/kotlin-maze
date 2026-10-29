package org.example.app

import org.example.app.database.mapper.MazeMapper
import org.example.app.database.repository.MazeFileRepository
import org.example.app.domain.algorithm.EllerMazeGenerator
import java.io.File
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class MazeFileRepositoryTest {
    @Test
    fun `save then load keeps maze`() {
        val repository = MazeFileRepository(MazeMapper())
        val maze = EllerMazeGenerator().generate(5, 5, Random(3))
        val file = File.createTempFile("maze_test", ".txt")
        file.deleteOnExit()
        try {
            repository.save(maze, file.absolutePath)
            val loaded = repository.load(file.absolutePath)
            assertTrue(loaded.rows == maze.rows && loaded.cols == maze.cols)
            assertTrue(loaded.verticalWalls.contentDeepEquals(maze.verticalWalls))
            assertTrue(loaded.horizontalWalls.contentDeepEquals(maze.horizontalWalls))
        } finally {
            file.delete()
        }
    }

    @Test
    fun `load rejects malformed file`() {
        val repository = MazeFileRepository(MazeMapper())
        val file = File.createTempFile("maze_test", ".txt")
        file.deleteOnExit()
        try {
            file.writeText("5 5\n0 1\n")
            assertFailsWith<IllegalArgumentException> { repository.load(file.absolutePath) }
        } finally {
            file.delete()
        }
    }

    @Test
    fun `text and back keeps the maze`() {
        // этим же текстом обменивается веб, поэтому проверяем отдельно
        val repository = MazeFileRepository(MazeMapper())
        for (size in listOf(1, 2, 10, 50)) {
            val maze = EllerMazeGenerator().generate(size, size, Random(size))
            val restored = repository.parse(repository.toText(maze))

            assertTrue(restored.rows == maze.rows && restored.cols == maze.cols)
            assertTrue(restored.verticalWalls.contentDeepEquals(maze.verticalWalls))
            assertTrue(restored.horizontalWalls.contentDeepEquals(maze.horizontalWalls))
        }
    }

    @Test
    fun `text of a non square maze is read back`() {
        val repository = MazeFileRepository(MazeMapper())
        val maze = EllerMazeGenerator().generate(3, 7, Random(1))
        val restored = repository.parse(repository.toText(maze))

        assertTrue(restored.rows == 3 && restored.cols == 7)
        assertTrue(restored.horizontalWalls.contentDeepEquals(maze.horizontalWalls))
    }

    @Test
    fun `text starts with the size and holds both matrices`() {
        val repository = MazeFileRepository(MazeMapper())
        val maze = EllerMazeGenerator().generate(4, 6, Random(2))

        val lines = repository.toText(maze).lines().filter { it.isNotBlank() }
        assertTrue(lines[0] == "4 6")
        assertTrue(lines.size == 1 + 4 * 2)
    }

    @Test
    fun `parse rejects text without size`() {
        val repository = MazeFileRepository(MazeMapper())
        assertFailsWith<IllegalArgumentException> { repository.parse("совсем не лабиринт") }
    }

    @Test
    fun `parse rejects a wrong number of rows`() {
        val repository = MazeFileRepository(MazeMapper())
        assertFailsWith<IllegalArgumentException> { repository.parse("3 3\n1 1 1\n1 1 1\n") }
    }

    @Test
    fun `parse rejects wall values other than 0 and 1`() {
        val repository = MazeFileRepository(MazeMapper())
        val text = "2 2\n0 5\n0 1\n\n1 1\n1 1\n"
        assertFailsWith<IllegalArgumentException> { repository.parse(text) }
    }
}
