import re

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'r') as f:
    content = f.read()

old_logic = """                    val seeds = _uiState.value.validIps.map { it.ip }"""

new_logic = """                    val seeds = (localIps + _uiState.value.validIps.map { it.ip }).distinct()"""

content = content.replace(old_logic, new_logic)

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'w') as f:
    f.write(content)

