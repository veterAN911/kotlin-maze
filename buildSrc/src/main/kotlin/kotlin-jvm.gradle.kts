// The code in this file is a convention plugin - a Gradle mechanism for sharing reusable build logic.
// `buildSrc` is a Gradle-recognized directory and every plugin there will be easily available in the rest of the build.
package buildsrc.convention

import org.gradle.api.tasks.testing.logging.TestLogEvent

plugins {
    // Apply the Kotlin JVM plugin to add support for Kotlin in JVM projects.
    kotlin("jvm")
    // JaCoCo считает, какая доля кода выполняется тестами (make coverage).
    jacoco
}

kotlin {
    // Use a specific Java version to make it easier to work in different environments.
    jvmToolchain(21)
}

dependencies {
    // Тесты пишутся на kotlin.test и запускаются на JUnit 5.
    // Начиная с Gradle 9 launcher платформы нужно подключать явно,
    // иначе тестовый процесс падает с «Failed to load JUnit Platform».
    "testImplementation"(platform("org.junit:junit-bom:5.10.2"))
    "testRuntimeOnly"("org.junit.platform:junit-platform-launcher")
}

// Отчёт о покрытии: HTML — для просмотра глазами, XML — чтобы можно было разобрать машинно.
tasks.withType<JacocoReport>().configureEach {
    reports {
        html.required = true
        xml.required = true
    }
}

tasks.withType<Test>().configureEach {
    // Configure all test Gradle tasks to use JUnitPlatform.
    useJUnitPlatform()

    // Log information about all test results, not only the failed ones.
    testLogging {
        events(
            TestLogEvent.FAILED,
            TestLogEvent.PASSED,
            TestLogEvent.SKIPPED
        )
    }
}
