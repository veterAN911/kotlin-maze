package org.example.app.domain.service

import org.example.app.database.repository.CaveRepository
import org.example.app.database.repository.MazeRepository
import org.example.app.domain.algorithm.CaveGenerator
import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.algorithm.MazeSolver
import org.example.app.domain.algorithm.QLearningAgent
import org.example.app.domain.model.Cave
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position

// сам ничего не делает, только передаёт работу дальше. экраны дёргают сервис и не
// знают кто там внутри
class GameService(
    private val generator: EllerMazeGenerator,
    private val repository: MazeRepository,
    private val solver: MazeSolver,
    private val caveGenerator: CaveGenerator,
    private val caveRepository: CaveRepository,
) : GameInterface {
    override fun generateMaze(
        rows: Int,
        cols: Int,
    ): Maze = generator.generate(rows, cols)

    override fun loadMaze(path: String): Maze = repository.load(path)

    override fun saveMaze(
        maze: Maze,
        path: String,
    ) = repository.save(maze, path)

    override fun parseMaze(text: String): Maze = repository.parse(text)

    override fun mazeToText(maze: Maze): String = repository.toText(maze)

    override fun solveMaze(
        maze: Maze,
        start: Position,
        end: Position,
    ): List<Position> = solver.solve(maze, start, end)

    override fun randomCave(
        rows: Int,
        cols: Int,
        chance: Int,
    ): Cave = caveGenerator.random(rows, cols, chance)

    override fun stepCave(
        cave: Cave,
        birthLimit: Int,
        deathLimit: Int,
    ): Cave = caveGenerator.step(cave, birthLimit, deathLimit)

    override fun loadCave(path: String): Cave = caveRepository.load(path)

    override fun saveCave(
        cave: Cave,
        path: String,
    ) = caveRepository.save(cave, path)

    // финиш у агента один на всё обучение, так в тз. проходы берём из goodEpisodes,
    // оно само смотрит на размер лабиринта
    override fun trainAgent(
        maze: Maze,
        end: Position,
    ): QLearningAgent {
        val agent = QLearningAgent(maze, end)
        agent.train(agent.goodEpisodes())
        return agent
    }

    override fun agentPath(
        agent: QLearningAgent,
        start: Position,
    ): List<Position> = agent.pathToEnd(start)
}
