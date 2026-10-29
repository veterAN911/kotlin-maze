# Makefile для проекта Maze (обёртка над Gradle Wrapper).
# Работает на macOS/Linux и Windows (Git Bash/MSYS или make из Chocolatey).

# На Windows переменная окружения OS = Windows_NT.
ifeq ($(OS),Windows_NT)
    GRADLE := gradlew.bat
    RM_RF := cmd /c rmdir /s /q
else
    GRADLE := ./gradlew
    RM_RF := rm -rf
endif

# Куда ставить приложение. По умолчанию — внутрь сборки, но каталог можно задать любой:
#   make install INSTALL_DIR=/tmp/maze
INSTALL_DIR ?= app/build/install/maze

# Каталог с документацией, которую генерирует цель dvi.
DVI_DIR := app/build/dokka/html

# clang-format для стилевого теста из materials/instructions. На macOS он лежит в
# Command Line Tools, а в PATH его нет, поэтому путь ищем сами. Можно задать свой:
#   make clang-format CLANG_FORMAT=clang-format
CLANG_FORMAT ?= $(shell command -v clang-format 2>/dev/null || echo /Library/Developer/CommandLineTools/usr/bin/clang-format)

# C-файлы, которые clang-format умеет разбирать. Весь код проекта пока на Kotlin,
# поэтому список обычно пустой — это нормально, цели ниже просто скажут об этом.
# Каталоги сборки исключаем, иначе find полезет в чужие исходники.
C_FILES := $(shell find . -type f \( -name '*.c' -o -name '*.h' -o -name '*.cpp' -o -name '*.hpp' \) -not -path './build/*' -not -path './app/build/*')

# build/ — директория с артефактами Gradle, поэтому все цели-команды
# обязательно объявляем .PHONY, иначе make будет считать их «готовыми».
.PHONY: all build run install uninstall clean dvi dist tests clang-format clang-format-format ktlint ktlint-format help ?

# Сборка проекта (компиляция + тесты).
all: build

build:
	$(GRADLE) build

# Запуск игры и веб-сервера одновременно.
run:
	$(GRADLE) run

# Установка приложения в INSTALL_DIR.
install:
	$(GRADLE) installDist -PinstallDir=$(INSTALL_DIR)

# Удаление установленного приложения.
uninstall:
	$(RM_RF) $(INSTALL_DIR)

# Очистка всех артефактов сборки.
clean:
	$(GRADLE) clean

# Документация из KDoc-комментариев. Открывать её не открываем —
# цель должна только собрать, а смотреть файл каждый может сам.
dvi:
	$(GRADLE) :app:dokkaHtml
	@echo "Документация собрана: $(DVI_DIR)/index.html"

# Дистрибутив (zip с приложением).
dist:
	$(GRADLE) distZip

# Запуск тестов.
tests:
	$(GRADLE) test

# Стилевой тест из materials/instructions, настройки лежат в .clang-format.
# Без -Werror clang-format просто печатает замечания и возвращает ноль, поэтому
# сборка бы не падала. Без файлов он вообще читает stdin и висит, поэтому пустой
# список ловим отдельно. Сейчас в проекте весь код на Kotlin, а clang-format его
# не разбирает (принимает .kt за C++ и ругается на каждую строку), так что
# проверять тут пока нечего. Появятся .c/.h — цель сразу начнёт их гонять.
# Файлы цель не меняет, только ругается.
clang-format:
	@if [ -z "$(C_FILES)" ]; then \
		echo "C-файлов нет, проверять нечего: код на Kotlin, clang-format его не разбирает"; \
		echo "Стиль Kotlin проверяет цель: make ktlint"; \
	elif ! command -v "$(CLANG_FORMAT)" > /dev/null 2>&1 && [ ! -x "$(CLANG_FORMAT)" ]; then \
		echo "clang-format не найден, поставь его: brew install clang-format"; \
		exit 1; \
	else \
		$(CLANG_FORMAT) -n -Werror $(C_FILES) && echo "Стиль C-файлов в порядке"; \
	fi

# Поправить стиль C-файлов автоматом: clang-format -i перезаписывает файлы.
clang-format-format:
	@if [ -z "$(C_FILES)" ]; then \
		echo "C-файлов нет, править нечего: код на Kotlin, clang-format его не разбирает"; \
		echo "Стиль Kotlin правит цель: make ktlint-format"; \
	elif ! command -v "$(CLANG_FORMAT)" > /dev/null 2>&1 && [ ! -x "$(CLANG_FORMAT)" ]; then \
		echo "clang-format не найден, поставь его: brew install clang-format"; \
		exit 1; \
	else \
		$(CLANG_FORMAT) -i $(C_FILES) && echo "Стиль C-файлов поправлен"; \
	fi

# Стилевой тест для Kotlin, настройки в .editorconfig.
ktlint:
	$(GRADLE) :app:ktlintCheck

# Поправить стиль Kotlin автоматом, что ktlint умеет.
ktlint-format:
	$(GRADLE) :app:ktlintFormat

# Справка по всем целям. Второе имя — просто знак вопроса, чтобы набирать короче.
# В zsh знак вопроса это маска, поэтому его надо брать в кавычки: make '?'
help ?:
	@echo "Цели проекта Maze:"
	@echo ""
	@echo "  make build              собрать проект (компиляция + тесты)"
	@echo "  make run                запустить игру и веб-сервер"
	@echo "  make install            установить приложение в INSTALL_DIR"
	@echo "  make uninstall          удалить установленное приложение"
	@echo "  make clean              очистить артефакты сборки"
	@echo "  make dvi                собрать документацию в HTML"
	@echo "  make dist               собрать дистрибутив (zip)"
	@echo "  make tests              запустить тесты"
	@echo ""
	@echo "  make clang-format       проверить стиль C-файлов (ничего не меняет)"
	@echo "  make clang-format-format  поправить стиль C-файлов автоматом"
	@echo "  make ktlint             проверить стиль Kotlin"
	@echo "  make ktlint-format      поправить стиль Kotlin автоматом"
	@echo ""
	@echo "  make help, make '?'     эта справка"
