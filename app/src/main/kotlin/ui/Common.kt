package org.example.app.ui

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.width
import androidx.compose.material.OutlinedTextField
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.example.app.domain.model.Maze
import java.awt.FileDialog
import java.awt.Frame

// пускаем только цифры, иначе в поле залезет минус или буква и toIntOrNull вернёт
// null там где мы этого не ждём
@Composable
fun NumberField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(label)
        Spacer(modifier = Modifier.width(4.dp))
        OutlinedTextField(
            value = value,
            onValueChange = { onValueChange(it.filter { ch -> ch.isDigit() }) },
            modifier = Modifier.width(64.dp),
            singleLine = true,
        )
    }
}

// человек вводит от единицы а внутри всё с нуля, поэтому перед передачей в логику
// надо вычесть единицу, иначе уедешь на клетку вбок
fun inMaze(
    maze: Maze,
    row: Int,
    col: Int,
): Boolean = row in 1..maze.rows && col in 1..maze.cols

// системный диалог выбора файла. блокирующий, код встанет и будет ждать пока
// человек не выберет файл или не закроет окно
fun chooseFile(
    title: String,
    save: Boolean,
): String? {
    val dialog =
        FileDialog(
            null as Frame?,
            title,
            if (save) FileDialog.SAVE else FileDialog.LOAD,
        )
    dialog.isVisible = true
    return dialog.files.firstOrNull()?.absolutePath
}
