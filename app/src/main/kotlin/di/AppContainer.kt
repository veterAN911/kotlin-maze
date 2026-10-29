package org.example.app.di

import org.example.app.database.mapper.MazeMapper
import org.example.app.database.repository.CaveFileRepository
import org.example.app.database.repository.CaveRepository
import org.example.app.database.repository.MazeFileRepository
import org.example.app.database.repository.MazeRepository
import org.example.app.domain.algorithm.CaveGenerator
import org.example.app.domain.algorithm.EllerMazeGenerator
import org.example.app.domain.algorithm.MazeSolver
import org.example.app.domain.service.GameInterface
import org.example.app.domain.service.GameService
import org.example.app.ui.mapper.MazeUiMapper

// собираем всё в одном месте, никаких DI-библиотек. главное не создавать эти же
// классы где-то ещё, иначе будут две копии и поведение разъедется
object AppContainer {
    private val mapper = MazeMapper()
    private val generator = EllerMazeGenerator()
    private val solver = MazeSolver()
    private val caveGenerator = CaveGenerator()
    val mazeUiMapper = MazeUiMapper()

    val repository: MazeRepository = MazeFileRepository(mapper)
    val caveRepository: CaveRepository = CaveFileRepository()

    val game: GameInterface =
        GameService(
            generator = generator,
            repository = repository,
            solver = solver,
            caveGenerator = caveGenerator,
            caveRepository = caveRepository,
        )
}
