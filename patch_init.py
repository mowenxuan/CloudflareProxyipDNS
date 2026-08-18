import re

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'r') as f:
    content = f.read()

old_init = """        viewModelScope.launch {
            val prefs = application.dataStore.data.first()
            _uiState.update { state ->
                state.copy(
                    concurrentThreads = prefs[THREADS_KEY] ?: 100f,
                    maxLatency = prefs[LATENCY_KEY] ?: 350f,
                    targetIpCount = prefs[TARGET_IP_KEY] ?: 2000f,
                    targetValidIpCount = prefs[TARGET_VALID_KEY] ?: 10f,
                    targetAllValidIpCount = prefs[TARGET_ALL_VALID_KEY] ?: 100f,
                    workerApiUrl = prefs[API_URL_KEY] ?: "proxyipsinp.xxxxxxx.nyc.mn",
                    dataCenterFilter = prefs[DATACENTER_FILTER_KEY] ?: "ALL"
                )
            }
        }
        
        // Load initial IPs from database into the UI state
        viewModelScope.launch {
            repository.allIps.collect { ips ->
                if (!_uiState.value.isScanning && _uiState.value.validIps.isEmpty()) {
                    _uiState.update { it.copy(validIps = ips) }
                }
            }
        }"""

new_init = """        viewModelScope.launch {
            val prefs = application.dataStore.data.first()
            _uiState.update { state ->
                val savedFilter = prefs[DATACENTER_FILTER_KEY] ?: "ALL"
                state.copy(
                    concurrentThreads = prefs[THREADS_KEY] ?: 100f,
                    maxLatency = prefs[LATENCY_KEY] ?: 350f,
                    targetIpCount = prefs[TARGET_IP_KEY] ?: 2000f,
                    targetValidIpCount = prefs[TARGET_VALID_KEY] ?: 10f,
                    targetAllValidIpCount = prefs[TARGET_ALL_VALID_KEY] ?: 100f,
                    workerApiUrl = prefs[API_URL_KEY] ?: "proxyipsinp.xxxxxxx.nyc.mn",
                    dataCenterFilter = savedFilter,
                    activeFilter = savedFilter
                )
            }
        }
        
        // Load initial IPs from database into the UI state
        viewModelScope.launch {
            repository.allIps.collect { ips ->
                if (!_uiState.value.isScanning) {
                    _uiState.update { it.copy(validIps = ips) }
                }
            }
        }"""

content = content.replace(old_init, new_init)

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'w') as f:
    f.write(content)

