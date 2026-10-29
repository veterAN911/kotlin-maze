package org.example.app

import org.example.app.domain.algorithm.CaveGenerator
import org.example.app.domain.model.Cave
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class CaveGeneratorTest {
    @Test
    fun `random cave has the requested size`() {
        val cave = CaveGenerator().random(rows = 10, cols = 20, chance = 50, random = Random(1))
        assertEquals(10, cave.rows)
        assertEquals(20, cave.cols)
    }

    @Test
    fun `without our own random the game takes the usual one`() {
        val cave = CaveGenerator().random(rows = 10, cols = 12, chance = 50)
        assertEquals(10, cave.rows)
        assertEquals(12, cave.cols)
    }

    @Test
    fun `chance 0 gives an empty cave and chance 100 gives a solid one`() {
        val empty = CaveGenerator().random(10, 10, chance = 0, random = Random(1))
        assertTrue(empty.cells.all { row -> row.all { it == 0 } })

        val solid = CaveGenerator().random(10, 10, chance = 100, random = Random(1))
        assertTrue(solid.cells.all { row -> row.all { it == 1 } })
    }

    @Test
    fun `chance sets roughly the requested share of live cells`() {
        val cave = CaveGenerator().random(50, 50, chance = 50, random = Random(42))
        val alive = cave.cells.sumOf { row -> row.count { it == 1 } }
        val share = alive * 100 / (50 * 50)
        assertTrue(share in 40..60, "живых клеток $share%, ожидалось около 50%")
    }

    @Test
    fun `maximum size 50x50 works`() {
        val cave = CaveGenerator().random(50, 50, chance = 45, random = Random(3))
        assertEquals(50, cave.rows)
        assertEquals(50, CaveGenerator().step(cave, 4, 3).cols)
    }

    @Test
    fun `size must be from 1 to 50 and chance from 0 to 100`() {
        assertFailsWith<IllegalArgumentException> { CaveGenerator().random(51, 10, 50) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().random(10, 51, 50) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().random(0, 10, 50) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().random(10, 0, 50) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().random(10, 10, 101) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().random(10, 10, -1) }
    }

    @Test
    fun `cells outside the cave count as alive`() {
        // у угла за границей лежат 5 соседей, у середины стороны 3, у центра ни одного
        val cave =
            caveOf(
                "000",
                "000",
                "000",
            )
        assertEquals(5, cave.aliveNeighbours(0, 0))
        assertEquals(3, cave.aliveNeighbours(0, 1))
        assertEquals(0, cave.aliveNeighbours(1, 1))
    }

    @Test
    fun `a live cell with too few live neighbours dies`() {
        val cave =
            caveOf(
                "00000",
                "00000",
                "00100",
                "00000",
                "00000",
            )
        // предел рождения 7 не даёт ожить ни одной клетке (больше всего живых
        // соседей 5, у углов), поэтому вся пещера становится пустой
        val next = CaveGenerator().step(cave, birthLimit = 7, deathLimit = 1)
        assertFalse(next.isAlive(2, 2))
    }

    @Test
    fun `a live cell with enough live neighbours stays alive`() {
        val cave =
            caveOf(
                "00000",
                "00000",
                "00100",
                "00000",
                "00000",
            )
        // предел смерти 0, живая клетка не умирает никогда
        val next = CaveGenerator().step(cave, birthLimit = 0, deathLimit = 0)
        assertTrue(next.isAlive(2, 2))
    }

    @Test
    fun `a dead cell with enough live neighbours becomes alive`() {
        val cave =
            caveOf(
                "00000",
                "00100",
                "01010",
                "00100",
                "00000",
            )
        // центральная клетка мертва, вокруг четыре живых соседа
        assertTrue(CaveGenerator().step(cave, birthLimit = 3, deathLimit = 0).isAlive(2, 2))
        assertFalse(CaveGenerator().step(cave, birthLimit = 7, deathLimit = 0).isAlive(2, 2))
    }

    @Test
    fun `only the corners of an empty cave come alive`() {
        val cave =
            caveOf(
                "000",
                "000",
                "000",
            )
        // предел рождения 4, из пяти живых соседей за границей оживают только углы
        val next = CaveGenerator().step(cave, birthLimit = 4, deathLimit = 0)
        assertTrue(next.isAlive(0, 0) && next.isAlive(0, 2))
        assertTrue(next.isAlive(2, 0) && next.isAlive(2, 2))
        assertFalse(next.isAlive(0, 1))
        assertFalse(next.isAlive(1, 1))
    }

    @Test
    fun `limits must be from 0 to 7`() {
        val cave = caveOf("010", "101", "010")
        assertFailsWith<IllegalArgumentException> { CaveGenerator().step(cave, birthLimit = 8, deathLimit = 3) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().step(cave, birthLimit = -1, deathLimit = 3) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().step(cave, birthLimit = 3, deathLimit = 8) }
        assertFailsWith<IllegalArgumentException> { CaveGenerator().step(cave, birthLimit = 3, deathLimit = -1) }
    }

    @Test
    fun `step does not change the original cave`() {
        val cave = caveOf("010", "101", "010")
        val before = cave.cells.map { it.copyOf() }
        CaveGenerator().step(cave, birthLimit = 1, deathLimit = 1)
        assertTrue(before.indices.all { before[it].contentEquals(cave.cells[it]) })
    }

    @Test
    fun `a fully alive cave does not change`() {
        // у каждой клетки сплошной пещеры ровно 8 живых соседей, предел смерти 7
        // её не меняет
        val cave = CaveGenerator().random(5, 5, chance = 100, random = Random(1))
        assertTrue(cave.isSameAs(CaveGenerator().step(cave, birthLimit = 0, deathLimit = 7)))
    }

    @Test
    fun `simulation reaches a stable state`() {
        // тз требует чтобы через несколько шагов карта перестала меняться
        var cave = CaveGenerator().random(20, 20, chance = 45, random = Random(5))
        var steps = 0
        while (steps < 50) {
            val next = CaveGenerator().step(cave, birthLimit = 4, deathLimit = 3)
            if (cave.isSameAs(next)) break
            cave = next
            steps++
        }
        assertTrue(steps < 50, "пещера не стабилизировалась за 50 шагов")
    }

    // пещера из строк вида "0101", так тестовые случаи записывать нагляднее
    private fun caveOf(vararg lines: String): Cave =
        Cave(
            rows = lines.size,
            cols = lines[0].length,
            cells = lines.map { line -> IntArray(line.length) { line[it].digitToInt() } }.toTypedArray(),
        )
}
