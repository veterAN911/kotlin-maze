package org.example.app.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.Button
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import org.example.app.domain.model.Cave
import org.example.app.domain.service.GameInterface

private val ALIVE_COLOR = Color(0xFF2E2E2E)
private val DEAD_COLOR = Color.White

// вкладка пещеры. шаг это одна итерация автомата, авто это шаг раз в N миллисекунд
// чтобы глазами видеть как пещера меняется
@Composable
fun CaveScreen(game: GameInterface) {
    var cave by remember { mutableStateOf(game.randomCave(10, 10, 45)) }

    var rowsText by remember { mutableStateOf("10") }
    var colsText by remember { mutableStateOf("10") }
    var chanceText by remember { mutableStateOf("45") }
    var birthText by remember { mutableStateOf("4") }
    var deathText by remember { mutableStateOf("3") }
    var delayText by remember { mutableStateOf("500") }

    var running by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    fun step(): Boolean {
        val birth = birthText.toIntOrNull()
        val death = deathText.toIntOrNull()
        if (birth == null || death == null || birth !in 0..7 || death !in 0..7) {
            error = "Пределы рождения и смерти — числа от 0 до 7"
            running = false
            return false
        }
        cave = game.stepCave(cave, birth, death)
        error = null
        return true
    }

    // LaunchedEffect перезапускается когда меняется running или задержка. поэтому
    // если на ходу поправить задержку цикл не останется со старым числом
    val delayMs = delayText.toIntOrNull() ?: 500
    LaunchedEffect(running, delayMs) {
        while (running) {
            delay(delayMs.toLong())
            if (!step()) return@LaunchedEffect
        }
    }

    val generate: () -> Unit = {
        val rows = rowsText.toIntOrNull()
        val cols = colsText.toIntOrNull()
        val chance = chanceText.toIntOrNull()
        if (rows == null || cols == null || rows !in 1..50 || cols !in 1..50) {
            error = "Размеры пещеры — числа от 1 до 50"
        } else if (chance == null || chance !in 0..100) {
            error = "Шанс инициализации — число от 0 до 100"
        } else {
            cave = game.randomCave(rows, cols, chance)
            running = false
            error = null
        }
    }

    val load: () -> Unit = {
        val path = chooseFile("Загрузить пещеру", save = false)
        if (path != null) {
            try {
                cave = game.loadCave(path)
                rowsText = cave.rows.toString()
                colsText = cave.cols.toString()
                running = false
                error = null
            } catch (e: Exception) {
                error = "Не удалось загрузить файл: ${e.message}"
            }
        }
    }

    val save: () -> Unit = {
        val path = chooseFile("Сохранить пещеру", save = true)
        if (path != null) {
            try {
                game.saveCave(cave, path)
                error = null
            } catch (e: Exception) {
                error = "Не удалось сохранить файл: ${e.message}"
            }
        }
    }

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            NumberField("Строки:", rowsText) { rowsText = it }
            NumberField("Колонки:", colsText) { colsText = it }
            NumberField("Шанс:", chanceText) { chanceText = it }
            Text("%")
            Button(onClick = generate) { Text("Сгенерировать") }
        }

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            NumberField("Рождение:", birthText) { birthText = it }
            NumberField("Смерть:", deathText) { deathText = it }
            NumberField("Задержка:", delayText) { delayText = it }
            Text("мс")
            Button(onClick = { step() }) { Text("Шаг") }
            Button(onClick = { running = !running }) {
                Text(if (running) "Стоп" else "Авто")
            }
        }

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = load) { Text("Загрузить") }
            Button(onClick = save) { Text("Сохранить") }
        }

        error?.let { Text(it, color = Color(0xFFD32F2F)) }

        CaveCanvas(cave)
    }
}

// поле 500 на 500, живые клетки закрашены а мёртвые просто фон
@Composable
private fun CaveCanvas(cave: Cave) {
    Canvas(
        modifier =
            Modifier
                .size(FIELD_SIZE)
                .background(DEAD_COLOR),
    ) {
        val cellW = size.width / cave.cols
        val cellH = size.height / cave.rows

        for (row in 0 until cave.rows) {
            val top = row * cellH
            val bottom = (row + 1) * cellH
            for (col in 0 until cave.cols) {
                if (!cave.isAlive(row, col)) continue
                val left = col * cellW
                val right = (col + 1) * cellW
                drawRect(
                    color = ALIVE_COLOR,
                    topLeft = Offset(left, top),
                    size = Size(right - left, bottom - top),
                )
            }
        }
    }
}
