package org.example.app.domain.algorithm

import org.example.app.domain.model.Cave
import kotlin.random.Random

// пещеры клеточным автоматом. сыпем случайные стенки а потом много раз прогоняем
// step, поле само себя причёсывает
class CaveGenerator {
    // nextInt(100) даёт от 0 до 99 поэтому шанс 100 засыпет вообще всё а 0 ничего
    fun random(
        rows: Int,
        cols: Int,
        chance: Int,
        random: Random = Random.Default,
    ): Cave {
        require(rows in 1..50 && cols in 1..50) { "Размеры пещеры должны быть от 1 до 50" }
        require(chance in 0..100) { "Шанс инициализации должен быть от 0 до 100" }

        val cells = Array(rows) { IntArray(cols) { if (random.nextInt(100) < chance) 1 else 0 } }
        return Cave(rows, cols, cells)
    }

    // считаем в отдельный массив next, иначе будем менять пещеру прямо во время
    // обхода и вторая половина клеток посчитается уже по испорченным данным
    //
    // с неравенствами аккуратно, у живой alive < deathLimit а у мёртвой
    // alive > birthLimit. в тз именно строгое только у рождения, поставишь >= и
    // пещеры станут другими
    fun step(
        cave: Cave,
        birthLimit: Int,
        deathLimit: Int,
    ): Cave {
        require(birthLimit in 0..7) { "Предел рождения должен быть от 0 до 7" }
        require(deathLimit in 0..7) { "Предел смерти должен быть от 0 до 7" }

        val next = Array(cave.rows) { IntArray(cave.cols) }
        for (row in 0 until cave.rows) {
            for (col in 0 until cave.cols) {
                val alive = cave.aliveNeighbours(row, col)
                next[row][col] =
                    if (cave.isAlive(row, col)) {
                        if (alive < deathLimit) 0 else 1
                    } else {
                        if (alive > birthLimit) 1 else 0
                    }
            }
        }
        return Cave(cave.rows, cave.cols, next)
    }
}
