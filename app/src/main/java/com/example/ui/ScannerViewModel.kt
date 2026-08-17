package com.example.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.AppDatabase
import com.example.data.IpRepository
import com.example.data.ScannedIp
import com.example.scanner.ScannerEngine
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class ScannerViewModel(application: Application) : AndroidViewModel(application) {
    private val repository: IpRepository
    
    init {
        val database = AppDatabase.getDatabase(application)
        repository = IpRepository(database.scannedIpDao(), database.syncRuleDao())
    }

    val allSavedIps = repository.allIps
    val favoriteIps = repository.favoriteIps
    val allRules = repository.allRules

    private val _uiState = MutableStateFlow(ScannerUiState())
    val uiState: StateFlow<ScannerUiState> = _uiState.asStateFlow()

    private var scanJob: Job? = null
    private val listMutex = Mutex()

    fun updateApiUrl(url: String) {
        _uiState.update { it.copy(workerApiUrl = url) }
    }
    
    fun updateConcurrentThreads(threads: Float) {
        _uiState.update { it.copy(concurrentThreads = threads) }
    }
    
    fun updateMaxLatency(latency: Float) {
        _uiState.update { it.copy(maxLatency = latency) }
    }
    
    fun updateTargetIpCount(count: Float) {
        _uiState.update { it.copy(targetIpCount = count) }
    }
    
    fun updateDataCenterFilter(filter: String) {
        _uiState.update { it.copy(dataCenterFilter = filter) }
    }

    fun toggleScanMode() {
        _uiState.update { it.copy(useCloudApi = !it.useCloudApi) }
    }

    fun startScan() {
        if (_uiState.value.isScanning) return
        
        _uiState.update { it.copy(isScanning = true, scannedCount = 0, validIps = emptyList()) }
        
        scanJob = viewModelScope.launch(Dispatchers.Default) {
            val targetCount = _uiState.value.targetIpCount.toInt()
            val ipsToTest = ScannerEngine.generateRandomIps(targetCount)
            val useApi = _uiState.value.useCloudApi
            var apiUrl = _uiState.value.workerApiUrl.trim()
            if (apiUrl.isNotBlank() && !apiUrl.startsWith("http://") && !apiUrl.startsWith("https://")) {
                apiUrl = "https://$apiUrl"
            }
            val maxLatency = _uiState.value.maxLatency.toLong()
            val dataCenters = _uiState.value.dataCenterFilter.split(",").map { it.trim().uppercase() }.filter { it.isNotEmpty() && it != "ALL" }
            val chunkSize = _uiState.value.concurrentThreads.toInt()
            
            ipsToTest.chunked(chunkSize).forEach { chunk ->
                if (!isActive) return@forEach
                
                val jobs = chunk.map { ip ->
                    launch {
                        val result = if (useApi && apiUrl.isNotBlank()) {
                            ScannerEngine.testIpViaApi(apiUrl, ip)
                        } else {
                            ScannerEngine.testIp(ip)
                        }
                        
                        listMutex.withLock {
                            _uiState.update { state ->
                                state.copy(scannedCount = state.scannedCount + 1)
                            }
                            if (result != null && result.latency <= maxLatency) {
                                val coloMatches = dataCenters.isEmpty() || dataCenters.contains(result.colo.uppercase())
                                if (coloMatches) {
                                    val scannedIp = ScannedIp(
                                        ip = result.ip,
                                        colo = result.colo,
                                        latency = result.latency
                                    )
                                    // Make sure it is stored in the database locally so it shows in StorageScreen
                                    repository.insertIp(scannedIp)
                                    // Also mark it as favorite immediately to show up in the favoriteIps Flow
                                    repository.updateFavorite(scannedIp.ip, true)
                                    
                                    _uiState.update { state ->
                                        val currentValid = state.validIps.toMutableList()
                                        val existingIndex = currentValid.indexOfFirst { it.ip == scannedIp.ip }
                                        if (existingIndex == -1) {
                                            val index = currentValid.indexOfFirst { it.latency > scannedIp.latency }
                                            if (index == -1) currentValid.add(scannedIp) else currentValid.add(index, scannedIp)
                                        } else if (scannedIp.latency < currentValid[existingIndex].latency) {
                                            currentValid.removeAt(existingIndex)
                                            val index = currentValid.indexOfFirst { it.latency > scannedIp.latency }
                                            if (index == -1) currentValid.add(scannedIp) else currentValid.add(index, scannedIp)
                                        }
                                        state.copy(validIps = currentValid)
                                    }
                                }
                            }
                        }
                    }
                }
                jobs.forEach { it.join() }
                
                // Trim local storage to max 100
                repository.trimTo100Latest()
            }
            
            _uiState.update { it.copy(isScanning = false) }
            performAutoSync()
        }
    }

    private fun performAutoSync() {
        viewModelScope.launch {
            val autoRules = repository.getAutoSyncRules()
            for (rule in autoRules) {
                syncRule(rule)
            }
        }
    }

    fun syncRule(rule: com.example.data.CloudflareSyncRule) {
        viewModelScope.launch {
            try {
                val colos = rule.coloFilter.split(",").map { it.trim().uppercase() }.filter { it.isNotEmpty() }
                val ipsToSync = repository.getIpsByColo(colos, rule.syncCount)
                val success = com.example.scanner.CloudflareSyncEngine.syncRule(rule, ipsToSync)
                
                val updatedRule = rule.copy(
                    lastSyncTime = System.currentTimeMillis(),
                    lastSyncStatus = if (success) "同步成功" else "同步失败"
                )
                repository.updateRule(updatedRule)
            } catch (e: Exception) {
                val updatedRule = rule.copy(
                    lastSyncTime = System.currentTimeMillis(),
                    lastSyncStatus = "同步出错: ${e.message}"
                )
                repository.updateRule(updatedRule)
            }
        }
    }

    fun saveRule(rule: com.example.data.CloudflareSyncRule) {
        viewModelScope.launch {
            if (rule.id == 0) {
                repository.insertRule(rule)
            } else {
                repository.updateRule(rule)
            }
        }
    }

    fun deleteRule(rule: com.example.data.CloudflareSyncRule) {
        viewModelScope.launch {
            repository.deleteRule(rule)
        }
    }

    fun toggleRuleAutoSync(rule: com.example.data.CloudflareSyncRule) {
        viewModelScope.launch {
            repository.updateRule(rule.copy(isAutoSync = !rule.isAutoSync))
        }
    }

    fun stopScan() {
        scanJob?.cancel()
        _uiState.update { it.copy(isScanning = false) }
    }

    fun toggleFavorite(ip: ScannedIp) {
        viewModelScope.launch {
            repository.updateFavorite(ip.ip, !ip.isFavorite)
            _uiState.update { state ->
                val currentValid = state.validIps.map {
                    if (it.ip == ip.ip) it.copy(isFavorite = !it.isFavorite) else it
                }
                state.copy(validIps = currentValid)
            }
        }
    }

    fun setFilter(colo: String) {
        _uiState.update { it.copy(activeFilter = colo) }
    }

    fun clearAll() {
        viewModelScope.launch {
            repository.clearAll()
            _uiState.update { it.copy(validIps = emptyList()) }
        }
    }

    private val _queryState = MutableStateFlow(QueryUiState())
    val queryState: StateFlow<QueryUiState> = _queryState.asStateFlow()

    fun queryDomainOrIp(input: String) {
        if (input.isBlank()) return
        _queryState.update { it.copy(isLoading = true, results = emptyList(), error = null) }

        viewModelScope.launch {
            try {
                // If it looks like an IP or has a port, test it directly
                val portRemote = if (input.contains(":")) input.substringAfterLast(":").toIntOrNull() ?: 443 else 443
                val cleanInput = input.substringBeforeLast(":")
                
                val useApi = _uiState.value.useCloudApi
                var apiUrl = _uiState.value.workerApiUrl.trim()
                if (apiUrl.isNotBlank() && !apiUrl.startsWith("http://") && !apiUrl.startsWith("https://")) {
                    apiUrl = "https://$apiUrl"
                }

                if (cleanInput.matches(Regex("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")) || 
                    cleanInput.contains("[")) {
                    val result = if (useApi && apiUrl.isNotBlank()) ScannerEngine.testIpViaApi(apiUrl, cleanInput, portRemote) else ScannerEngine.testIp(cleanInput, portRemote)
                    val info = ScannerEngine.getIpInfo(cleanInput)
                    _queryState.update { 
                        it.copy(
                            isLoading = false,
                            results = listOf(QueryResult(cleanInput, result?.colo, result?.latency, info?.country, info?.asn))
                        )
                    }
                } else {
                    // Resolve domain first
                    val ips = ScannerEngine.resolveDomain(cleanInput)
                    if (ips.isEmpty()) {
                        _queryState.update { it.copy(isLoading = false, error = "未能解析出 IP 地址") }
                        return@launch
                    }
                    
                    val results = mutableListOf<QueryResult>()
                    ips.forEach { ip ->
                        val result = if (useApi && apiUrl.isNotBlank()) ScannerEngine.testIpViaApi(apiUrl, ip, portRemote) else ScannerEngine.testIp(ip, portRemote)
                        if (result != null) {
                            val info = ScannerEngine.getIpInfo(ip)
                            results.add(QueryResult(ip, result.colo, result.latency, info?.country, info?.asn))
                            // Update UI incrementally
                            _queryState.update { it.copy(results = results.toList()) }
                        }
                    }
                    _queryState.update { it.copy(isLoading = false) }
                }
            } catch (e: Exception) {
                _queryState.update { it.copy(isLoading = false, error = e.message ?: "查询失败") }
            }
        }
    }
}

data class QueryUiState(
    val isLoading: Boolean = false,
    val results: List<QueryResult> = emptyList(),
    val error: String? = null
)

data class QueryResult(
    val ip: String,
    val colo: String?,
    val latency: Long?,
    val country: String?,
    val asn: String?
)

data class ScannerUiState(
    val isScanning: Boolean = false,
    val scannedCount: Int = 0,
    val validIps: List<ScannedIp> = emptyList(),
    val activeFilter: String = "ALL",
    val useCloudApi: Boolean = true,
    val workerApiUrl: String = "proxyipsinp.xxxxxxx.nyc.mn",
    val concurrentThreads: Float = 100f,
    val maxLatency: Float = 350f,
    val targetIpCount: Float = 2000f,
    val dataCenterFilter: String = "ALL"
) {
    val displayedIps: List<ScannedIp>
        get() = if (activeFilter == "ALL") validIps else validIps.filter { it.colo == activeFilter }
}
