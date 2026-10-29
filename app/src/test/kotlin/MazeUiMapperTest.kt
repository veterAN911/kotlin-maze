package org.example.app

import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import org.example.app.ui.mapper.MazeUiMapper
import org.example.app.ui.mapper.UiLine
import org.example.app.ui.mapper.UiPoint
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class MazeUiMapperTest {
    private val mapper = MazeUiMapper()

    // тот же лабиринт что и в тесте решателя, открыты (0,0)-(0,1), (0,1)-(1,1)
    // и (1,1)-(1,0)
    private val maze =
        Maze(
            rows = 2,
            cols = 2,
            verticalWalls = arrayOf(intArrayOf(0, 1), intArrayOf(0, 1)),
            horizontalWalls = arrayOf(intArrayOf(1, 0), intArrayOf(1, 1)),
        )

    @Test
    fun `walls are drawn where the walls are`() {
        val lines = mapper.wallLines(maze)

        assertTrue(UiLine(0f, 0f, 2f, 0f) in lines, "нет верхней границы")
        assertTrue(UiLine(0f, 0f, 0f, 2f) in lines, "нет левой границы")
        assertTrue(UiLine(2f, 0f, 2f, 1f) in lines, "нет вертикальной стены")
        assertTrue(UiLine(0f, 1f, 1f, 1f) in lines, "нет горизонтальной стены")
    }

    @Test
    fun `only the walls from the maze are drawn`() {
        // границы 2, вертикальные (0,1) и (1,1), горизонтальные (0,0), (1,0), (1,1)
        assertEquals(7, mapper.wallLines(maze).size)
    }

    @Test
    fun `the maze takes the whole field`() {
        // границы совпали с краями поля, значит клетки растянуты на всё поле
        val big = EllerMazeGenerator().generate(7, 4, Random(5))
        val lines = mapper.wallLines(big)

        assertTrue(UiLine(0f, 0f, 4f, 0f) in lines, "верхняя граница не по краю поля")
        assertTrue(UiLine(0f, 0f, 0f, 7f) in lines, "левая граница не по краю поля")
    }

    @Test
    fun `every maze gets its border lines`() {
        // в файле верхней и левой границы нет, их дорисовывает отрисовка
        for (size in listOf(1, 2, 10)) {
            val lines = mapper.wallLines(EllerMazeGenerator().generate(size, size, Random(size)))
            assertTrue(UiLine(0f, 0f, size.toFloat(), 0f) in lines, "нет верхней границы у $size x $size")
            assertTrue(UiLine(0f, 0f, 0f, size.toFloat()) in lines, "нет левой границы у $size x $size")
        }
    }

    @Test
    fun `the route goes through the middle of the cells`() {
        val points = mapper.pathPoints(listOf(Position(0, 0), Position(2, 3), Position(1, 1)))

        assertEquals(
            listOf(UiPoint(0.5f, 0.5f), UiPoint(3.5f, 2.5f), UiPoint(1.5f, 1.5f)),
            points,
        )
    }

    @Test
    fun `an empty route has no points`() {
        assertEquals(emptyList(), mapper.pathPoints(emptyList()))
    }
}
