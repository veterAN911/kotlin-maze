plugins {
    // Общая настройка JVM-модулей (версия Java и запуск тестов) из buildSrc.
    id("buildsrc.convention.kotlin-jvm")
    id("org.jetbrains.compose") version "1.6.0"
    // Dokka генерирует HTML-документацию из KDoc-комментариев (цель make dvi).
    id("org.jetbrains.dokka") version "1.9.20"
    // Стилевой тест для kotlin. clang-format из материалов его не разбирает,
    // поэтому для котлина берём ktlint, а clang-format оставляем проверять C
    id("org.jlleitschuh.gradle.ktlint") version "14.2.0"
    application
}

repositories {
    mavenCentral()
    google()
}

dependencies {
    implementation(compose.desktop.currentOs)
    implementation(libs.ktorServerCore)
    implementation(libs.ktorServerNetty)
    testImplementation(kotlin("test"))
    // Поднимает сервер Ktor прямо в тесте, без сети и портов.
    testImplementation(libs.ktorServerTestHost)
}

application {
    mainClass = "org.example.app.LauncherKt"
    // Имя установленного приложения: app/build/install/maze
    applicationName = "maze"
}

// Каталог установки. По умолчанию — внутри сборки, но его можно переопределить:
//   make install INSTALL_DIR=/любой/другой/каталог
val installDir = providers.gradleProperty("installDir")
tasks.named<Sync>("installDist") {
    if (installDir.isPresent) {
        into(installDir.get())
    }
}
