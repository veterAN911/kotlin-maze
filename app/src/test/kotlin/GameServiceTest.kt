package org.example.app

import org.example.app.database.mapper.MazeMapper
import org.example.app.database.repository.CaveFileRepository
import org.example.app.database.repository.MazeFileRepository
import org.example.app.domain.algorithm.CaveGenerator
import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.algorithm.MazeSolver
import org.example.app.domain.model.Position
import org.example.app.domain.service.GameService
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class GameServiceTest {
    private val game =
        GameService(
            EllerMazeGenerator(),
            MazeFileRepository(MazeMapper()),
            MazeSolver(),
            CaveGenerator(),
            CaveFileRepository(),
        )

    @Test
    fun `trained agent walks from every cell to the fixed finish`() {
        repeat(3) {
            val maze = game.generateMaze(10, 10)
            val end = Position(9, 9)
            val agent = game.trainAgent(maze, end)

            assertTrue(agent.episodesDone > 0, "обучение не выполнилось")

            for (row in 0 until maze.rows) {
                for (col in 0 until maze.cols) {
                    val start = Position(row, col)
                    val route = game.agentPath(agent, start)
                    assertEquals(start, route.firstOrNull(), "маршрут не начинается в $start")
                    assertEquals(end, route.lastOrNull(), "маршрут из $start не дошёл до финиша")
                    // лабиринт идеальный, между двумя клетками путь только один,
                    // поэтому маршрут агента обязан совпасть с решением bfs
                    assertEquals(game.solveMaze(maze, start, end), route, "маршрут из $start не кратчайший")
                }
            }
        }
    }

    @Test
    fun `the route from the finish is the finish itself`() {
        val maze = game.generateMaze(8, 8)
        val end = Position(4, 4)
        val agent = game.trainAgent(maze, end)

        assertEquals(listOf(end), game.agentPath(agent, end))
    }

    @Test
    fun `the agent keeps the maze and the finish it was trained on`() {
        val maze = game.generateMaze(6, 6)
        val end = Position(0, 5)
        val agent = game.trainAgent(maze, end)

        // финиш закреплён при обучении, из любой точки маршрут ведёт именно туда
        assertEquals(end, game.agentPath(agent, Position(5, 0)).last())
        assertEquals(end, game.agentPath(agent, Position(3, 3)).last())
    }
}
