import re

with open('app/src/main/java/com/example/ui/Screens.kt', 'r') as f:
    content = f.read()

replacement = """@Composable
fun IpCard(ip: ScannedIp, onToggleFavorite: (ScannedIp) -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp).fillMaxWidth()) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Text(ip.ip, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                Spacer(modifier = Modifier.weight(1f))
                Text(
                    text = java.text.SimpleDateFormat("MM-dd HH:mm", java.util.Locale.getDefault()).format(java.util.Date(ip.timestamp)),
                    fontSize = 12.sp,
                    color = TextSecondary
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(4.dp))
                            .background(PrimaryOrange.copy(alpha = 0.2f))
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    ) {
                        Text(ip.colo, fontSize = 12.sp, color = PrimaryOrange, fontWeight = FontWeight.Bold)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(getColoLocation(ip.colo), fontSize = 14.sp, color = TextSecondary)
                }
                
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(Color(0xFF332B1A))
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text("${ip.latency} ms", color = LatencyYellow, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
                
                Spacer(modifier = Modifier.width(12.dp))
                Icon(Icons.Rounded.Router, contentDescription = null, tint = IconBlue, modifier = Modifier.size(20.dp))
                Spacer(modifier = Modifier.width(4.dp))
                IconButton(onClick = { onToggleFavorite(ip) }, modifier = Modifier.size(32.dp)) {
                    Icon(
                        if (ip.isFavorite) Icons.Filled.Favorite else Icons.Filled.FavoriteBorder,
                        contentDescription = "Favorite",
                        tint = if (ip.isFavorite) PrimaryOrange else TextSecondary,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }
        }
    }
}"""

pattern = r"@Composable\s*fun IpCard.*?^}"
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.MULTILINE)

with open('app/src/main/java/com/example/ui/Screens.kt', 'w') as f:
    f.write(new_content)
