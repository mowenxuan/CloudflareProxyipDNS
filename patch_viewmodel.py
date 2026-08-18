import re

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'r') as f:
    content = f.read()

content = content.replace(
    'private val API_URL_KEY = stringPreferencesKey("api_url")',
    'private val API_URL_KEY = stringPreferencesKey("api_url")\n    private val DATACENTER_FILTER_KEY = stringPreferencesKey("datacenter_filter")'
)

content = content.replace(
    'workerApiUrl = prefs[API_URL_KEY] ?: "proxyipsinp.xxxxxxx.nyc.mn"',
    'workerApiUrl = prefs[API_URL_KEY] ?: "proxyipsinp.xxxxxxx.nyc.mn",\n                    dataCenterFilter = prefs[DATACENTER_FILTER_KEY] ?: "ALL"'
)

replace_func = """    fun updateDataCenterFilter(filter: String) {
        _uiState.update { it.copy(dataCenterFilter = filter) }
    }"""
new_func = """    fun updateDataCenterFilter(filter: String) {
        _uiState.update { it.copy(dataCenterFilter = filter.uppercase()) }
        viewModelScope.launch { getApplication<Application>().dataStore.edit { it[DATACENTER_FILTER_KEY] = filter.uppercase() } }
    }"""

content = content.replace(replace_func, new_func)

with open('app/src/main/java/com/example/ui/ScannerViewModel.kt', 'w') as f:
    f.write(content)

