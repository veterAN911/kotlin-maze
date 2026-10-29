package org.example.app.web

import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.server.application.Application
import io.ktor.server.application.ApplicationCall
import io.ktor.server.application.call
import io.ktor.server.request.receiveText
import io.ktor.server.response.respondText
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import org.example.app.domain.model.Maze
import org.example.app.domain.model.Position
import org.example.app.domain.service.GameInterface

// веб-часть. страница и Vue лежат обычными файлами, а всю работу с лабиринтом
// делает то же ядро на котлине что и в окошке. поэтому в js нет ни одного
// алгоритма, страница только рисует что сервер прислал
//
//   GET  /                        страница
//   GET  /vue.global.prod.js      vue, лежит локально, интернет не нужен
//   GET  /api/maze?rows=&cols=    сгенерировать
//   POST /api/maze                лабиринт из тела запроса, там текст формата тз
//   POST /api/solve?...           маршрут внутри присланного лабиринта
//
// ответ на первые два это {"maze":..., "text":"..."}, где text тот самый файл
// формата тз, страница отдаёт его на скачивание как есть
//
// координаты в решении с нуля, как во внутренней модели
class WebServer(
    private val game: GameInterface,
) {
    private val htmlPage: String = readResource("/web/index.html") ?: "<h1>Maze</h1>"
    private val vueScript: String = readResource("/web/vue.global.prod.js") ?: ""

    fun routes(): Application.() -> Unit =
        {
            routing {
                get("/") {
                    call.respondText(htmlPage, ContentType.Text.Html)
                }

                get("/vue.global.prod.js") {
                    call.respondText(vueScript, ContentType.Text.JavaScript)
                }

                // размеры из адреса приводим к 1..50, чтобы из браузера нельзя было
                // попросить лабиринт на миллион клеток и уронить приложение
                get("/api/maze") {
                    val rows =
                        call.request.queryParameters["rows"]
                            ?.toIntOrNull()
                            ?.coerceIn(1, 50) ?: 10
                    val cols =
                        call.request.queryParameters["cols"]
                            ?.toIntOrNull()
                            ?.coerceIn(1, 50) ?: 10
                    call.respondText(mazeAnswer(game.generateMaze(rows, cols)), ContentType.Application.Json)
                }

                post("/api/maze") {
                    val maze =
                        try {
                            game.parseMaze(call.receiveText())
                        } catch (e: Exception) {
                            call.badRequest("Не удалось прочитать лабиринт: ${e.message}")
                            return@post
                        }
                    call.respondText(mazeAnswer(maze), ContentType.Application.Json)
                }

                post("/api/solve") {
                    val startRow = call.request.queryParameters["startRow"]?.toIntOrNull()
                    val startCol = call.request.queryParameters["startCol"]?.toIntOrNull()
                    val endRow = call.request.queryParameters["endRow"]?.toIntOrNull()
                    val endCol = call.request.queryParameters["endCol"]?.toIntOrNull()

                    if (startRow == null || startCol == null || endRow == null || endCol == null) {
                        call.badRequest("Координаты точек должны быть целыми числами")
                        return@post
                    }

                    val maze =
                        try {
                            game.parseMaze(call.receiveText())
                        } catch (e: Exception) {
                            call.badRequest("Не удалось прочитать лабиринт: ${e.message}")
                            return@post
                        }

                    if (!inside(maze, startRow, startCol) || !inside(maze, endRow, endCol)) {
                        call.badRequest("Точка вне лабиринта: строка 0..${maze.rows - 1}, столбец 0..${maze.cols - 1}")
                        return@post
                    }

                    val path = game.solveMaze(maze, Position(startRow, startCol), Position(endRow, endCol))
                    call.respondText("{\"path\":${pathToJson(path)}}", ContentType.Application.Json)
                }
            }
        }

    private fun mazeAnswer(maze: Maze): String = "{\"maze\":${mazeToJson(maze)},\"text\":${textToJson(game.mazeToText(maze))}}"

    private suspend fun ApplicationCall.badRequest(message: String) {
        respondText(
            "{\"error\":${textToJson(message)}}",
            ContentType.Application.Json,
            HttpStatusCode.BadRequest,
        )
    }

    private fun inside(
        maze: Maze,
        row: Int,
        col: Int,
    ): Boolean = row in 0 until maze.rows && col in 0 until maze.cols

    // json собираем руками, без библиотеки. матрицы стен лежат как массивы массивов
    // чисел, поэтому строки просто склеиваем через запятую
    private fun mazeToJson(maze: Maze): String =
        buildString {
            append("{\"rows\":").append(maze.rows).append(",\"cols\":").append(maze.cols)
            append(",\"verticalWalls\":[")
            maze.verticalWalls.forEachIndexed { index, row ->
                if (index > 0) append(',')
                append('[').append(row.joinToString(",")).append(']')
            }
            append("],\"horizontalWalls\":[")
            maze.horizontalWalls.forEachIndexed { index, row ->
                if (index > 0) append(',')
                append('[').append(row.joinToString(",")).append(']')
            }
            append("]}")
        }

    private fun pathToJson(path: List<Position>): String = path.joinToString(",", "[", "]") { "[${it.row},${it.col}]" }

    // строку тоже руками экранируем, без этого кавычка или перевод строки в тексте
    // порвут json и браузер не разберёт ответ
    private fun textToJson(value: String): String =
        buildString {
            append('"')
            for (ch in value) {
                when (ch) {
                    '"' -> append("\\\"")
                    '\\' -> append("\\\\")
                    '\n' -> append("\\n")
                    '\r' -> append("\\r")
                    '\t' -> append("\\t")
                    else -> append(ch)
                }
            }
            append('"')
        }

    private fun readResource(path: String): String? =
        WebServer::class.java.getResourceAsStream(path)?.use { it.readBytes().toString(Charsets.UTF_8) }
}
