package org.example.app.database.repository

import org.example.app.domain.model.Cave

interface CaveRepository {
    fun load(path: String): Cave

    fun save(
        cave: Cave,
        path: String,
    )
}
