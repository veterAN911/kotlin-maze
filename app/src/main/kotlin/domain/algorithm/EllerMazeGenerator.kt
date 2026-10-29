package org.example.app.domain.algorithm

import org.example.app.domain.model.Maze
import kotlin.random.Random

// эллер. лабиринт выходит идеальный то есть между любыми двумя клетками ровно
// один путь, петель и отрезанных кусков нет
class EllerMazeGenerator {
    fun generate(
        rows: Int,
        cols: Int,
        random: Random = Random.Default,
    ): Maze {
        require(rows in 1..50 && cols in 1..50) { "Размеры лабиринта должны быть от 1 до 50" }

        // sets это номера множеств клеток в текущей строке, одинаковый номер значит
        // клетки уже соединены между собой
        val vertical = Array(rows) { IntArray(cols) { 1 } }
        val horizontal = Array(rows) { IntArray(cols) { 1 } }
        val sets = IntArray(cols) { it }
        var nextSet = cols

        for (r in 0 until rows - 1) {
            // рвём правые стены только между РАЗНЫМИ множествами, иначе получится
            // петля и лабиринт перестанет быть идеальным
            for (c in 0 until cols - 1) {
                if (sets[c] != sets[c + 1] && random.nextBoolean()) {
                    vertical[r][c] = 0
                    mergeSets(sets, sets[c + 1], sets[c])
                }
            }

            // снизу тоже рвём наугад но потом обязательно проверяем что у каждого
            // множества остался хоть один проход вниз, а то целые куски лабиринта
            // окажутся отрезанными от нижней части
            val setsWithOpening = mutableSetOf<Int>()
            for (c in 0 until cols) {
                val open = random.nextBoolean()
                horizontal[r][c] = if (open) 0 else 1
                if (open) setsWithOpening.add(sets[c])
            }
            for (c in 0 until cols) {
                if (sets[c] !in setsWithOpening) {
                    horizontal[r][c] = 0
                    setsWithOpening.add(sets[c])
                }
            }

            // у кого нет прохода вниз тот дальше один, поэтому даём новые номера
            for (c in 0 until cols) {
                if (horizontal[r][c] == 1) sets[c] = nextSet++
            }
        }

        // из последней строки вниз уже некуда, поэтому просто рвём правые стены
        // подряд пока все множества не сольются в одно
        for (c in 0 until cols - 1) {
            if (sets[c] != sets[c + 1]) {
                vertical[rows - 1][c] = 0
                mergeSets(sets, sets[c + 1], sets[c])
            }
        }

        return Maze(rows, cols, vertical, horizontal)
    }

    private fun mergeSets(
        sets: IntArray,
        from: Int,
        to: Int,
    ) {
        for (i in sets.indices) {
            if (sets[i] == from) sets[i] = to
        }
    }
}
