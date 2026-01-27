def analyze_node(cpu):
    if cpu > 85: return ("HARMFUL", "#ff4d4d", "AI: Critical load. Suggesting reroute.")
    if cpu > 60: return ("WARNING", "#ffa64d", "AI: Moderate stress detected.")
    return ("HEALTHY", "#00ff88", "AI: System operating normally.")