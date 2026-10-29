package org.example.app

import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.HttpStatusCode
import io.ktor.server.testing.ApplicationTestBuilder
import io.ktor.server.testing.testApplication
import org.example.app.database.mapper.MazeMapper
import org.example.app.database.repository.CaveFileRepository
import org.example.app.database.repository.MazeFileRepository
import org.example.app.domain.algorithm.CaveGenerator
import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.algorithm.MazeSolver
import org.example.app.domain.service.GameService
import org.example.app.web.WebServer
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class WebServerTest {
    private val server =
        WebServer(
            GameService(
                EllerMazeGenerator(),
                MazeFileRepository(MazeMapper()),
                MazeSolver(),
                CaveGenerator(),
                CaveFileRepository(),
            ),
        )

    // цепляем маршруты к тестовому приложению, настоящий сервер с портом для
    // тестов поднимать не надо
    private fun ApplicationTestBuilder.withRoutes() {
        val routes = server.routes()
        application { routes() }
    }

    // тот же лабиринт 2x2 что в тесте решателя, путь (0,0)-(0,1)-(1,1)-(1,0)
    private val mazeText = "2 2\n0 1\n0 1\n\n1 0\n1 1\n"

    @Test
    fun `the page is served`() =
        testApplication {
            withRoutes()
            val answer = client.get("/")
            assertEquals(HttpStatusCode.OK, answer.status)
            assertTrue(answer.bodyAsText().contains("id=\"app\""), "на странице нет приложения Vue")
        }

    @Test
    fun `vue is served`() =
        testApplication {
            withRoutes()
            val answer = client.get("/vue.global.prod.js")
            assertEquals(HttpStatusCode.OK, answer.status)
            assertTrue(answer.bodyAsText().contains("vue"))
        }

    @Test
    fun `generate returns the asked size`() =
        testApplication {
            withRoutes()
            val answer = client.get("/api/maze?rows=4&cols=6")
            assertEquals(HttpStatusCode.OK, answer.status)

            val body = answer.bodyAsText()
            assertTrue(body.contains("\"rows\":4"), "неверное число строк: $body")
            assertTrue(body.contains("\"cols\":6"), "неверное число столбцов: $body")
            assertTrue(body.contains("\"text\""), "в ответе нет текста лабиринта")
        }

    @Test
    fun `generate without size gives 10x10`() =
        testApplication {
            withRoutes()
            val body = client.get("/api/maze").bodyAsText()
            assertTrue(body.contains("\"rows\":10") && body.contains("\"cols\":10"), body)
        }

    @Test
    fun `solve returns the shortest route`() =
        testApplication {
            withRoutes()
            val answer =
                client.post("/api/solve?startRow=0&startCol=0&endRow=1&endCol=0") {
                    setBody(mazeText)
                }
            assertEquals(HttpStatusCode.OK, answer.status)
            assertEquals("{\"path\":[[0,0],[0,1],[1,1],[1,0]]}", answer.bodyAsText())
        }

    @Test
    fun `solve from a point to itself gives one cell`() =
        testApplication {
            withRoutes()
            val answer =
                client.post("/api/solve?startRow=1&startCol=0&endRow=1&endCol=0") {
                    setBody(mazeText)
                }
            assertEquals(HttpStatusCode.OK, answer.status)
            assertEquals("{\"path\":[[1,0]]}", answer.bodyAsText())
        }

    @Test
    fun `solve rejects a point outside the maze`() =
        testApplication {
            withRoutes()
            val answer =
                client.post("/api/solve?startRow=0&startCol=0&endRow=5&endCol=5") {
                    setBody(mazeText)
                }
            assertEquals(HttpStatusCode.BadRequest, answer.status)
            assertTrue(answer.bodyAsText().contains("вне лабиринта"), answer.bodyAsText())
        }

    @Test
    fun `solve rejects broken coordinates`() =
        testApplication {
            withRoutes()
            val answer =
                client.post("/api/solve?startRow=abc&startCol=0&endRow=1&endCol=0") {
                    setBody(mazeText)
                }
            assertEquals(HttpStatusCode.BadRequest, answer.status)
            assertTrue(answer.bodyAsText().contains("целыми числами"), answer.bodyAsText())
        }

    @Test
    fun `solve rejects a broken maze`() =
        testApplication {
            withRoutes()
            val answer =
                client.post("/api/solve?startRow=0&startCol=0&endRow=1&endCol=0") {
                    setBody("это не лабиринт")
                }
            assertEquals(HttpStatusCode.BadRequest, answer.status)
            assertTrue(answer.bodyAsText().contains("Не удалось прочитать"), answer.bodyAsText())
        }

    @Test
    fun `upload reads the maze from the body`() =
        testApplication {
            withRoutes()
            val answer = client.post("/api/maze") { setBody(mazeText) }
            assertEquals(HttpStatusCode.OK, answer.status)

            val body = answer.bodyAsText()
            assertTrue(body.contains("\"rows\":2") && body.contains("\"cols\":2"), body)
            // в ответе должен лежать тот же текст что прислали
            assertTrue(body.contains("2 2\\n0 1\\n0 1"), "текст лабиринта потерялся: $body")
        }

    @Test
    fun `upload rejects a broken file`() =
        testApplication {
            withRoutes()
            val answer = client.post("/api/maze") { setBody("5 5\n0 1\n") }
            assertEquals(HttpStatusCode.BadRequest, answer.status)
        }
}
