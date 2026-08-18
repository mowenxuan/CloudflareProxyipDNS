import re

with open('app/src/main/java/com/example/scanner/ScannerEngine.kt', 'r') as f:
    content = f.read()

content = content.replace("70% chance to expand", "90% chance to expand")
content = content.replace("30% chance to explore", "10% chance to explore")
content = content.replace("if (random.nextInt(100) < 70)", "if (random.nextInt(100) < 90)")

with open('app/src/main/java/com/example/scanner/ScannerEngine.kt', 'w') as f:
    f.write(content)

