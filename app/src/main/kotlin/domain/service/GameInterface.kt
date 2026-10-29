package org.example.app.domain.service

import org.example.app.domain.algorithm.QLearningAgent
import org.example.app.domain.model.Cave
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position

interface GameInterface {
    fun generateMaze(
        rows: Int,
        cols: Int,
    ): Maze

    fun loadMaze(path: String): Maze

    fun saveMaze(
        maze: Maze,
        path: String,
    )

    // эти две нужны только для веба. формат тз умеет разбирать только котлин,
    // поэтому страница гоняет готовый текст и сама в него не лезет
    fun parseMaze(text: String): Maze

    fun mazeToText(maze: Maze): String

    fun solveMaze(
        maze: Maze,
        start: Position,
        end: Position,
    ): List<Position>

    fun randomCave(
        rows: Int,
        cols: Int,
        chance: Int,
    ): Cave

    fun stepCave(
        cave: Cave,
        birthLimit: Int,
        deathLimit: Int,
    ): Cave

    fun loadCave(path: String): Cave

    fun saveCave(
        cave: Cave,
        path: String,
    )

    // проходы не передаём снаружи, агент сам считает их от размеров лабиринта,
    // иначе каждый экран начнёт придумывать своё число
    fun trainAgent(
        maze: Maze,
        end: Position,
    ): QLearningAgent

    fun agentPath(
        agent: QLearningAgent,
        start: Position,
    ): List<Position>
}
