package org.example.app

import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import org.example.app.di.AppContainer
import org.example.app.web.WebServer
import java.awt.Desktop
import java.net.ServerSocket
import java.net.URI
import kotlin.concurrent.thread

// точка входа, поднимает веб-сервер и окошко сразу. порт можно задать через PORT,
// по умолчанию 9090. сервер в фоновом потоке и демон, поэтому умрёт вместе
// с приложением
fun main() {
    val host = System.getenv("HOST") ?: "0.0.0.0"
    val wantPort = System.getenv("PORT")?.toIntOrNull() ?: 9090
    val port = freePort(wantPort)
    if (port != wantPort) {
        println("Порт $wantPort занят, использую $port")
    }

    val webServer = WebServer(game = AppContainer.game)
    thread(name = "web-server", isDaemon = true) {
        embeddedServer(Netty, port = port, host = host, module = webServer.routes()).start(wait = true)
    }

    val url = "http://localhost:$port"
    println("Веб-интерфейс: $url")
    openBrowser(url)
    desktopApp()
}

// ищем свободный порт начиная с заданного, занятые пропускаем. сделано чтобы
// второй запуск не падал с ошибкой а просто взял порт рядом
private fun freePort(start: Int): Int {
    for (port in start until start + 100) {
        try {
            ServerSocket(port).use { return port }
        } catch (e: Exception) {
            // порт занят, пробуем следующий
        }
    }
    return start
}

// открываем страницу в браузере. если графической оболочки нет то просто скажем
// человеку адрес, ронять приложение из-за этого незачем
private fun openBrowser(url: String) {
    try {
        if (Desktop.isDesktopSupported() && Desktop.getDesktop().isSupported(Desktop.Action.BROWSE)) {
            Desktop.getDesktop().browse(URI(url))
        }
    } catch (e: Exception) {
        println("Откройте вручную: $url")
    }
}
