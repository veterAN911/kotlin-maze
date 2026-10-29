package org.example.app

import org.example.app.database.repository.CaveFileRepository
import org.example.app.domain.algorithm.CaveGenerator
import java.io.File
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class CaveFileRepositoryTest {
    @Test
    fun `save then load keeps cave`() {
        val repository = CaveFileRepository()
        val cave = CaveGenerator().random(10, 12, chance = 40, random = Random(9))
        val file = File.createTempFile("cave_test", ".txt")
        file.deleteOnExit()
        try {
            repository.save(cave, file.absolutePath)
            val loaded = repository.load(file.absolutePath)
            assertTrue(cave.isSameAs(loaded))
        } finally {
            file.delete()
        }
    }

    @Test
    fun `load reads the example from the specification`() {
        val file =
            tempCaveFile(
                """
                4 4
                0 1 0 1
                1 0 0 1
                0 1 0 0
                0 0 1 1
                """.trimIndent(),
            )
        try {
            val cave = CaveFileRepository().load(file.absolutePath)
            assertEquals(4, cave.rows)
            assertEquals(4, cave.cols)
            assertTrue(cave.isAlive(0, 1))
            assertTrue(cave.isAlive(3, 2))
            assertTrue(!cave.isAlive(0, 0))
            assertTrue(!cave.isAlive(1, 2))
        } finally {
            file.delete()
        }
    }

    @Test
    fun `load accepts 1x1 cave`() {
        val file = tempCaveFile("1 1\n1\n")
        try {
            val cave = CaveFileRepository().load(file.absolutePath)
            assertEquals(1, cave.rows)
            assertTrue(cave.isAlive(0, 0))
            // клетка одна, вокруг неё всё за границей а оно считается живым
            assertEquals(8, cave.aliveNeighbours(0, 0))
        } finally {
            file.delete()
        }
    }

    @Test
    fun `load accepts 50x50 cave`() {
        val rows = (1..50).joinToString("\n") { (1..50).joinToString(" ") { "0" } }
        val file = tempCaveFile("50 50\n$rows\n")
        try {
            val cave = CaveFileRepository().load(file.absolutePath)
            assertEquals(50, cave.rows)
            assertEquals(50, cave.cols)
        } finally {
            file.delete()
        }
    }

    @Test
    fun `rejects wrong cell values`() {
        val file = tempCaveFile("2 2\n0 1\n2 0\n")
        try {
            assertFailsWith<IllegalArgumentException> { CaveFileRepository().load(file.absolutePath) }
        } finally {
            file.delete()
        }
    }

    @Test
    fun `rejects size over 50`() {
        val file = tempCaveFile("51 2\n0 1\n")
        try {
            assertFailsWith<IllegalArgumentException> { CaveFileRepository().load(file.absolutePath) }
        } finally {
            file.delete()
        }
    }

    @Test
    fun `rejects malformed file`() {
        val file = tempCaveFile("4 4\n0 1\n")
        try {
            assertFailsWith<IllegalArgumentException> { CaveFileRepository().load(file.absolutePath) }
        } finally {
            file.delete()
        }
    }

    // временный файл с готовым текстом, чтобы каждый раз не писать одно и то же
    private fun tempCaveFile(text: String): File {
        val file = File.createTempFile("cave_test", ".txt")
        file.deleteOnExit()
        file.writeText(text)
        return file
    }
}
