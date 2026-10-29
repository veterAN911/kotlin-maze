package org.example.app

import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.algorithm.QLearningAgent
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class QLearningAgentTest {
    @Test
    fun `after training the agent leaves every cell of a 10x10 maze`() {
        val maze = EllerMazeGenerator().generate(10, 10, Random(11))
        val end = Position(9, 9)
        val agent = QLearningAgent(maze, end, Random(7))
        agent.train(agent.goodEpisodes())

        for (row in 0 until maze.rows) {
            for (col in 0 until maze.cols) {
                val start = Position(row, col)
                val path = agent.pathToEnd(start)
                assertTrue(path.isNotEmpty(), "агент не нашёл выход из $start")
                assertEquals(start, path.first())
                assertEquals(end, path.last())
            }
        }
    }

    @Test
    fun `after training the agent leaves every cell of a 20x20 maze`() {
        val maze = EllerMazeGenerator().generate(20, 20, Random(12))
        val end = Position(19, 19)
        val agent = QLearningAgent(maze, end, Random(7))
        agent.train(agent.goodEpisodes())

        var notFound = 0
        for (row in 0 until maze.rows) {
            for (col in 0 until maze.cols) {
                if (agent.pathToEnd(Position(row, col)).isEmpty()) notFound++
            }
        }
        assertEquals(0, notFound, "агент не нашёл выход из $notFound клеток")
    }

    @Test
    fun `the route goes only through open passages`() {
        val maze = EllerMazeGenerator().generate(7, 7, Random(3))
        val agent = QLearningAgent(maze, Position(6, 6), Random(5))
        agent.train(agent.goodEpisodes())

        val path = agent.pathToEnd(Position(0, 0))
        assertTrue(path.isNotEmpty(), "агент не нашёл выход")
        for (i in 0 until path.size - 1) {
            assertTrue(maze.canGo(path[i], path[i + 1]), "ход ${path[i]} -> ${path[i + 1]} через стену")
        }
    }

    @Test
    fun `the route never visits the same cell twice`() {
        val maze = EllerMazeGenerator().generate(8, 8, Random(4))
        val agent = QLearningAgent(maze, Position(0, 7), Random(9))
        agent.train(agent.goodEpisodes())

        val path = agent.pathToEnd(Position(7, 0))
        assertTrue(path.isNotEmpty(), "агент не нашёл выход")
        assertEquals(path.size, path.toSet().size, "в маршруте есть повторяющиеся клетки")
    }

    @Test
    fun `the route from the goal is just the goal`() {
        val maze = EllerMazeGenerator().generate(5, 5, Random(1))
        val end = Position(4, 4)
        val agent = QLearningAgent(maze, end)

        assertEquals(listOf(end), agent.pathToEnd(end))
    }

    @Test
    fun `the same seed gives the same route`() {
        val maze = EllerMazeGenerator().generate(6, 6, Random(2))
        val end = Position(5, 5)

        val first = QLearningAgent(maze, end, Random(7))
        first.train(5_000)
        val second = QLearningAgent(maze, end, Random(7))
        second.train(5_000)

        assertEquals(first.pathToEnd(Position(0, 0)), second.pathToEnd(Position(0, 0)))
    }

    @Test
    fun `training counts the passes`() {
        val maze = EllerMazeGenerator().generate(5, 5, Random(1))
        val agent = QLearningAgent(maze, Position(4, 4))

        assertEquals(0, agent.episodesDone)
        agent.train(1_000)
        assertEquals(1_000, agent.episodesDone)
        agent.train(500)
        assertEquals(1_500, agent.episodesDone)
    }

    @Test
    fun `a maze of one cell does not hang training`() {
        val maze = EllerMazeGenerator().generate(1, 1, Random(1))
        val agent = QLearningAgent(maze, Position(0, 0))

        agent.train(10)

        assertEquals(10, agent.episodesDone)
        assertEquals(listOf(Position(0, 0)), agent.pathToEnd(Position(0, 0)))
    }

    @Test
    fun `zero or negative passes are rejected`() {
        val maze = EllerMazeGenerator().generate(5, 5, Random(1))
        val agent = QLearningAgent(maze, Position(4, 4))

        assertFailsWith<IllegalArgumentException> { agent.train(0) }
        assertFailsWith<IllegalArgumentException> { agent.train(-5) }
        assertEquals(0, agent.episodesDone)
    }

    @Test
    fun `small mazes always get the least number of passes`() {
        val small = QLearningAgent(EllerMazeGenerator().generate(5, 5), Position(4, 4))
        val big = QLearningAgent(EllerMazeGenerator().generate(30, 30), Position(29, 29))

        assertEquals(50_000, small.goodEpisodes())
        assertTrue(big.goodEpisodes() > 50_000, "для большого лабиринта нужно больше проходов")
    }

    @Test
    fun `a maze without passages gives no route`() {
        // одни стены, выйти из клетки некуда
        val maze =
            Maze(
                rows = 2,
                cols = 2,
                verticalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
                horizontalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
            )
        val agent = QLearningAgent(maze, Position(1, 1), Random(1))
        agent.train(1_000)

        assertEquals(emptyList(), agent.pathToEnd(Position(0, 0)))
    }

    @Test
    fun `an untrained agent does not know the way`() {
        // агент не сделал ни одного прохода, таблица пустая и ходы случайные.
        // из середины открытого поля он кружит по пройденным клеткам и сдаётся
        val maze =
            Maze(
                rows = 5,
                cols = 5,
                verticalWalls = Array(5) { IntArray(5) },
                horizontalWalls = Array(5) { IntArray(5) },
            )
        val agent = QLearningAgent(maze, Position(4, 4), Random(1))

        assertEquals(emptyList(), agent.pathToEnd(Position(2, 2)))
    }

    @Test
    fun `an unreachable finish gives no route and does not hang`() {
        // верхние две клетки соединены между собой но отрезаны от нижней строки
        // где лежит финиш. агент должен сдаться а не кружить вечно
        val maze =
            Maze(
                rows = 2,
                cols = 2,
                verticalWalls = arrayOf(intArrayOf(0, 1), intArrayOf(1, 1)),
                horizontalWalls = arrayOf(intArrayOf(1, 1), intArrayOf(1, 1)),
            )
        val agent = QLearningAgent(maze, Position(1, 1), Random(3))
        agent.train(1_000)

        assertEquals(emptyList(), agent.pathToEnd(Position(0, 0)))
        assertEquals(emptyList(), agent.pathToEnd(Position(0, 1)))
    }
}
