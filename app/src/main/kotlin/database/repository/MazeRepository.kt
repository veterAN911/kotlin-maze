package org.example.app.database.repository

import org.example.app.domain.model.Maze

interface MazeRepository {
    fun load(path: String): Maze

    fun save(
        maze: Maze,
        path: String,
    )

    // тот же формат тз только текстом в памяти, нужно для веба
    fun parse(text: String): Maze

    fun toText(maze: Maze): String
}
