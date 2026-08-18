import re

with open('app/src/main/java/com/example/ui/Screens.kt', 'r') as f:
    content = f.read()

replacement = """                    Slider(
                        value = uiState.targetIpCount,
                        onValueChange = { viewModel.updateTargetIpCount(it) },
                        valueRange = 100f..3000f,
                        colors = SliderDefaults.colors(thumbColor = PrimaryOrange, activeTrackColor = PrimaryOrange)
                    )
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    OutlinedTextField(
                        value = uiState.dataCenterFilter,
                        onValueChange = { viewModel.updateDataCenterFilter(it) },
                        label = { Text("数据中心过滤器 (如 HKG,SJC,LAX)", color = TextSecondary) },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary)
                    )

                    Spacer(modifier = Modifier.height(24.dp))
                    OutlinedTextField(
                        value = uiState.workerApiUrl,"""

pattern = r"                    Slider\(\s*value = uiState\.targetIpCount,.*?colors = SliderDefaults\.colors\(thumbColor = PrimaryOrange, activeTrackColor = PrimaryOrange\)\s*\)\s*Spacer\(modifier = Modifier\.height\(24\.dp\)\)\s*OutlinedTextField\(\s*value = uiState\.workerApiUrl,"

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('app/src/main/java/com/example/ui/Screens.kt', 'w') as f:
    f.write(content)

