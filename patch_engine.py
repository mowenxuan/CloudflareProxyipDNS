import re

with open('app/src/main/java/com/example/scanner/ScannerEngine.kt', 'r') as f:
    content = f.read()

new_func = """    fun generateIpsAroundSeeds(seeds: List<String>, count: Int): List<String> {
        val ips = mutableListOf<String>()
        val random = Random.Default
        if (seeds.isEmpty()) return generateRandomIps(count)
        
        for (i in 0 until count) {
            // 70% chance to expand around a known seed, 30% chance to explore totally random
            if (random.nextInt(100) < 70) {
                val seed = seeds[random.nextInt(seeds.size)]
                val parts = seed.split(".")
                if (parts.size == 4) {
                    val newIp = if (random.nextBoolean()) {
                        // /24 expansion
                        "${parts[0]}.${parts[1]}.${parts[2]}.${random.nextInt(256)}"
                    } else {
                        // /16 expansion
                        "${parts[0]}.${parts[1]}.${random.nextInt(256)}.${random.nextInt(256)}"
                    }
                    ips.add(newIp)
                } else {
                    ips.addAll(generateRandomIps(1))
                }
            } else {
                ips.addAll(generateRandomIps(1))
            }
        }
        return ips
    }

    fun generateRandomIps"""

content = content.replace("    fun generateRandomIps", new_func)

with open('app/src/main/java/com/example/scanner/ScannerEngine.kt', 'w') as f:
    f.write(content)

