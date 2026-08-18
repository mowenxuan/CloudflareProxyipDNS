import re

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'r') as f:
    content = f.read()

old_logic = """                val ipsToTest = if (isFirstRound && localIps.isNotEmpty()) {
                    isFirstRound = false
                    localIps
                } else {
                    isFirstRound = false
                    ScannerEngine.generateRandomIps(ipsToGeneratePerRound)
                }"""

new_logic = """                val ipsToTest = if (isFirstRound && localIps.isNotEmpty()) {
                    isFirstRound = false
                    localIps
                } else {
                    isFirstRound = false
                    val seeds = _uiState.value.validIps.map { it.ip }
                    if (seeds.isNotEmpty()) {
                        ScannerEngine.generateIpsAroundSeeds(seeds, ipsToGeneratePerRound)
                    } else {
                        ScannerEngine.generateRandomIps(ipsToGeneratePerRound)
                    }
                }"""

content = content.replace(old_logic, new_logic)

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'w') as f:
    f.write(content)

