package org.example.app.database.model

data class MazeFileModel(
    val rows: Int,
    val cols: Int,
    val verticalWalls: List<List<Int>>,
    val horizontalWalls: List<List<Int>>,
)
