#!/usr/bin/env python3
"""
🚀 Inktrace Template Setup Script
setup_templates.py

Quick script to set up the template structure if files are missing.
"""

import os
from pathlib import Path

def create_directories():
    """Create required directories"""
    dirs = [
        "templates",
        "static/css", 
        "static/js",
        "static/images"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def create_basic_dashboard_template():
    """Create a basic dashboard template if missing"""
    template_path = Path("templates/dashboard.html")
    
    if template_path.exists():
        print(f"✅ Template already exists: {template_path}")
        return
    
    basic_template = '''<!DOCTYPE html>
<html>
<head>
    <title>🐙 Inktrace Agent Inspector</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/static/css/dashboard.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐙 Inktrace Agent Inspector</h1>
            <div class="tagline">Uncover hidden threats. One agent at a time.</div>
        </div>
        
        <nav class="nav">
            <a href="/" class="active">🏠 Dashboard</a>
            <a href="/communications">🔍 Communications</a>
            <a href="/security-events">📊 Security Events</a>
            <a href="/api/agents" target="_blank">🔌 API</a>
        </nav>
        
        <div class="dashboard-grid">
            <div class="card">
                <div class="card-title">
                    <span class="card-title-icon">🤖</span>
                    Discovered Agents
                </div>
                {% for agent_id, agent in agents.items() %}
                <div class="agent-item">
                    <div class="agent-name">{{ agent.name or 'Unknown' }}</div>
                    <div class="agent-details">Port: {{ agent.port }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="card">
                <div class="card-title">
                    <span class="card-title-icon">🛡️</span>
                    Security Status
                </div>
                <div>Threat Level: {{ threat_level or 'LOW' }}</div>
                <div>Malicious Agents: {{ malicious_count or 0 }}</div>
            </div>
        </div>
    </div>
    
    <script src="/static/js/dashboard.js"></script>
</body>
</html>'''
    
    with open(template_path, 'w') as f:
        f.write(basic_template)
    print(f"✅ Created basic template: {template_path}")

def create_basic_css():
    """Create basic CSS if missing"""
    css_path = Path("static/css/dashboard.css")
    
    if css_path.exists():
        print(f"✅ CSS already exists: {css_path}")
        return
    
    basic_css = '''/* Basic Inktrace Dashboard Styles */
body {
    font-family: system-ui, -apple-system, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

.header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem;
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 1rem;
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.nav {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.nav a {
    color: #e2e8f0;
    text-decoration: none;
    padding: 0.75rem 1.5rem;
    background: rgba(51, 65, 85, 0.6);
    border-radius: 0.75rem;
    border: 1px solid #475569;
}

.nav a:hover, .nav a.active {
    background: #3b82f6;
    border-color: #60a5fa;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 1.5rem;
}

.card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-radius: 1rem;
    border: 1px solid #475569;
    padding: 1.5rem;
}

.card-title {
    display: flex;
    align-items: center;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.card-title-icon {
    margin-right: 0.75rem;
    font-size: 1.5rem;
}

.agent-item {
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-radius: 0.5rem;
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid #374151;
}

.agent-name {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.agent-details {
    font-size: 0.8rem;
    color: #94a3b8;
}'''
    
    with open(css_path, 'w') as f:
        f.write(basic_css)
    print(f"✅ Created basic CSS: {css_path}")

def create_basic_js():
    """Create basic JavaScript if missing"""
    js_path = Path("static/js/dashboard.js")
    
    if js_path.exists():
        print(f"✅ JavaScript already exists: {js_path}")
        return
    
    basic_js = '''// Basic Inktrace Dashboard JavaScript
console.log('🐙 Inktrace Dashboard loaded');

// Auto-refresh dashboard every 5 seconds
setInterval(() => {
    // Simple refresh for basic functionality
    window.location.reload();
}, 5000);

// Basic WebSocket connection (if available)
try {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => console.log('🔗 WebSocket connected');
    ws.onclose = () => console.log('🔌 WebSocket disconnected');
    ws.onerror = (error) => console.log('❌ WebSocket error:', error);
} catch (error) {
    console.log('⚠️ WebSocket not available:', error);
}'''
    
    with open(js_path, 'w') as f:
        f.write(basic_js)
    print(f"✅ Created basic JavaScript: {js_path}")

def create_other_templates():
    """Create other basic templates"""
    templates = {
        "communications.html": '''<!DOCTYPE html>
<html>
<head>
    <title>🐙 Communications Monitor</title>
    <link rel="stylesheet" href="/static/css/dashboard.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐙 Communications Monitor</h1>
        </div>
        <nav class="nav">
            <a href="/">🏠 Dashboard</a>
            <a href="/communications" class="active">🔍 Communications</a>
            <a href="/security-events">📊 Security Events</a>
        </nav>
        <div class="card">
            <div class="card-title">📡 Agent Communications</div>
            <p>Communications monitoring active...</p>
        </div>
    </div>
</body>
</html>''',
        "security_events.html": '''<!DOCTYPE html>
<html>
<head>
    <title>🐙 Security Events</title>
    <link rel="stylesheet" href="/static/css/dashboard.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Security Events Monitor</h1>
        </div>
        <nav class="nav">
            <a href="/">🏠 Dashboard</a>
            <a href="/communications">🔍 Communications</a>
            <a href="/security-events" class="active">📊 Security Events</a>
        </nav>
        <div class="card">
            <div class="card-title">🚨 Security Events</div>
            <p>Security monitoring active...</p>
        </div>
    </div>
</body>
</html>'''
    }
    
    for filename, content in templates.items():
        template_path = Path(f"templates/{filename}")
        if not template_path.exists():
            with open(template_path, 'w') as f:
                f.write(content)
            print(f"✅ Created template: {template_path}")

def main():
    """Main setup function"""
    print("🚀 Setting up Inktrace template structure...")
    print("=" * 50)
    
    create_directories()
    create_basic_dashboard_template()
    create_basic_css()
    create_basic_js()
    create_other_templates()
    
    print("=" * 50)
    print("✅ Template setup complete!")
    print("\n🎯 Next steps:")
    print("1. Run: uv run python scripts/launch.py")
    print("2. Open: http://localhost:8003/dashboard")
    print("3. For full templates, copy the complete versions from the artifacts")
    print("\n🐙 Ready for hackathon demo!")

if __name__ == "__main__":
    main()