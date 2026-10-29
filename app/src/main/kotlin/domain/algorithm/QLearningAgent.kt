package org.example.app.domain.algorithm

import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import kotlin.random.Random

// агент который сам учится ходить по лабиринту, Q-обучение. состояние это клетка,
// действие шаг в одну из четырёх сторон, для каждой пары клетка+направление копится
// число насколько так шагать выгодно. сначала везде нули, потом агент тыщу раз
// бегает по лабиринту и сам расставляет числа по формуле
//   Q(s,a) = Q(s,a) + ALPHA * (награда + GAMMA * лучшее Q в новой клетке - Q(s,a))
// за шаг -1 за финиш 0 поэтому агенту выгодно где шагов меньше, вот и весь фокус
class QLearningAgent(
    private val maze: Maze,
    private val end: Position,
    private val random: Random = Random.Default,
) {
    private val q = Array(maze.rows * maze.cols) { DoubleArray(ACTIONS) }

    private val maxSteps = maze.rows * maze.cols * 4

    var episodesDone = 0
        private set

    // числа не из головы, замерял: для 50x50 надо около 375 тысяч проходов
    fun goodEpisodes(): Int = maxOf(MIN_EPISODES, maze.rows * maze.cols * EPISODES_PER_CELL)

    fun train(episodes: Int) {
        require(episodes > 0) { "Число проходов должно быть больше нуля" }

        for (episode in 0 until episodes) {
            val epsilon = MAX_EPSILON - (MAX_EPSILON - MIN_EPSILON) * episode / episodes
            trainEpisode(epsilon)
            episodesDone++
        }
    }

    private fun trainEpisode(epsilon: Double) {
        // из одной клетки стартовать неоткуда, без этого randomStart зациклится
        // намертво потому что финиш это единственная клетка
        if (maze.rows * maze.cols < 2) return

        var current = randomStart()
        var steps = 0

        while (current != end && steps < maxSteps) {
            val action = chooseAction(current, epsilon)
            val next = move(current, action)

            // на финише bestNext берём нулём а не из таблицы, иначе агент начнёт
            // считать финиш обычной клеткой и запутается
            val reward = if (next == end) FINISH_REWARD else STEP_REWARD
            val bestNext = if (next == end) 0.0 else q[index(next)].max()

            val old = q[index(current)][action]
            q[index(current)][action] = old + ALPHA * (reward + GAMMA * bestNext - old)

            current = next
            steps++
        }
    }

    fun pathToEnd(start: Position): List<Position> {
        val path = mutableListOf(start)
        val visited = mutableSetOf(start)
        var current = start

        // предела шагов тут нет и не надо, каждый шаг обязан попасть в НОВУЮ клетку
        // а клеток конечное число значит цикл сам кончится
        while (current != end) {
            val next = move(current, bestAction(current))
            // move вернул ту же клетку значит упёрлись в стену, либо вернулись куда
            // уже ходили. дороги агент не знает, сдаёмся. без этой проверки будем
            // кружить по одним и тем же клеткам до посинения
            if (next == current || !visited.add(next)) return emptyList()

            path.add(next)
            current = next
        }
        return path
    }

    private fun chooseAction(
        position: Position,
        epsilon: Double,
    ): Int = if (random.nextDouble() < epsilon) random.nextInt(ACTIONS) else bestAction(position)

    // одинаковых лучших направлений берём случайное, иначе агент всегда ходил бы
    // первым и застревал в одной и той же дороге
    private fun bestAction(position: Position): Int {
        val values = q[index(position)]
        val best = values.max()
        val bestActions = values.indices.filter { values[it] == best }
        return bestActions[random.nextInt(bestActions.size)]
    }

    // в стену и за границу нельзя, тогда возвращаем ту же клетку. шаги пишу прямо
    // тут а не двумя массивами сбоку, порядок тот же что в действиях
    // 0 вверх 1 вниз 2 влево 3 вправо
    private fun move(
        from: Position,
        action: Int,
    ): Position {
        val next =
            when (action) {
                0 -> Position(from.row - 1, from.col)
                1 -> Position(from.row + 1, from.col)
                2 -> Position(from.row, from.col - 1)
                else -> Position(from.row, from.col + 1)
            }
        return if (inMaze(next) && maze.canGo(from, next)) next else from
    }

    private fun randomStart(): Position {
        while (true) {
            val cell = Position(random.nextInt(maze.rows), random.nextInt(maze.cols))
            if (cell != end) return cell
        }
    }

    private fun inMaze(position: Position): Boolean = position.row in 0 until maze.rows && position.col in 0 until maze.cols

    private fun index(position: Position): Int = position.row * maze.cols + position.col

    private companion object {
        const val ACTIONS = 4

        // насколько новый опыт перебивает старый
        const val ALPHA = 0.1

        // насколько агент думает о будущем
        const val GAMMA = 0.9

        const val STEP_REWARD = -1.0
        const val FINISH_REWARD = 0.0

        const val MAX_EPSILON = 0.5
        const val MIN_EPSILON = 0.05

        const val EPISODES_PER_CELL = 150
        const val MIN_EPISODES = 50_000
    }
}
