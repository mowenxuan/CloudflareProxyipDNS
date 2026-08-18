import re

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'r') as f:
    content = f.read()

replace_func = """    fun setFilter(filter: String) {
        _uiState.update { it.copy(activeFilter = filter) }
    }"""
new_func = """    fun setFilter(filter: String) {
        _uiState.update { it.copy(activeFilter = filter) }
        // Synchronize with the scanner filter so next scan focuses on this
        updateDataCenterFilter(filter)
    }"""

content = content.replace(replace_func, new_func)

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'w') as f:
    f.write(content)

