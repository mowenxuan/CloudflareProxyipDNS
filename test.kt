import org.json.JSONObject

fun main() {
    val jsonString = """{
      "success": true,
      "proxyIP": "172.69.1.80",
      "portRemote": 443,
      "statusCode": 400,
      "responseSize": 414,
      "timestamp": "2026-08-17T16:25:57.053Z",
      "country": "LAX",
      "region": "Missouri",
      "city": "Kansas City",
      "isp": "Cloudflare, Inc.",
      "as": "AS13335 Cloudflare, Inc."
    }"""
    
    val json = JSONObject(jsonString)
    val fallback = json.optString("country", "UNK")
    println("fallback: $fallback")
    val colo = json.optString("colo", fallback)
    println("colo: $colo")
}
