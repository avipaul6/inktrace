// static/js/dashboard.js - Enhanced Real-Time Updates for Inktrace Dashboard

class InktraceDashboard {
    constructor() {
        this.websocket = null;
        this.retryCount = 0;
        this.maxRetries = 5;
        this.updateInterval = 2000; // Faster updates: 2 seconds
        this.lastUpdateTime = 0;
        
        this.init();
    }

    init() {
        console.log('🐙 Initializing Inktrace Dashboard with Enhanced Real-Time Updates');
        this.connectWebSocket();
        this.startDataRefresh();
        this.setupEventListeners();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('🔗 WebSocket connected for real-time updates');
                this.retryCount = 0;
                this.updateConnectionStatus('connected');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.updateConnectionStatus('disconnected');
                this.reconnectWebSocket();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.reconnectWebSocket();
        }
    }

    reconnectWebSocket() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            const delay = Math.min(1000 * Math.pow(2, this.retryCount), 10000);
            console.log(`🔄 Reconnecting WebSocket in ${delay}ms (attempt ${this.retryCount})`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            console.error('❌ Max WebSocket reconnection attempts reached');
            this.updateConnectionStatus('failed');
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message received:', data);
        
        // Trigger immediate dashboard refresh for any WebSocket message
        this.refreshDashboard();
        
        switch (data.type) {
            case 'agent_update':
                this.handleAgentUpdate(data.payload);
                break;
            case 'security_event':
                this.handleSecurityEvent(data.payload);
                break;
            case 'dashboard_refresh':
                this.refreshDashboard();
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    handleAgentUpdate(agent) {
        console.log('🤖 Agent updated via WebSocket:', agent);
        this.showNotification(`Agent Update: ${agent.name || 'Unknown'}`, 'info');
        // Force immediate refresh
        setTimeout(() => this.refreshDashboard(), 100);
    }

    handleSecurityEvent(event) {
        console.log('🚨 Security event via WebSocket:', event);
        const isCritical = event.type === 'malicious_agent_detected' || event.severity === 'critical';
        this.showNotification(
            `Security Alert: ${event.description || event.type}`, 
            isCritical ? 'critical' : 'warning'
        );
        // Force immediate refresh for security events
        setTimeout(() => this.refreshDashboard(), 100);
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = status.toUpperCase();
        }
    }

    async startDataRefresh() {
        console.log('🔄 Starting enhanced automatic data refresh');
        
        // Initial load
        await this.refreshDashboard();
        
        // Set up periodic refresh with faster updates
        setInterval(async () => {
            await this.refreshDashboard();
        }, this.updateInterval);
    }

    async refreshDashboard() {
        try {
            const currentTime = Date.now();
            // Prevent too frequent updates (debounce)
            if (currentTime - this.lastUpdateTime < 500) {
                return;
            }
            this.lastUpdateTime = currentTime;

            const response = await fetch('/api/dashboard-data');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.updateDashboardElements(data);
            
        } catch (error) {
            console.error('Failed to refresh dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    updateDashboardElements(data) {
        // Update ALL dashboard sections simultaneously
        this.updateAgentsList(data.agents || {});
        this.updateSecurityStatus(data);
        this.updateTentacleMatrix(data.tentacle_scores || []);
        this.updateRecentEvents(data.security_events || []);
        this.updateCriticalAlert(data.critical_alert);
        this.updateIntelligenceOverview(data);
        
        console.log('📊 ALL dashboard sections updated successfully');
    }

    updateAgentsList(agents) {
        const agentsContainer = document.getElementById('agents-list');
        if (!agentsContainer) return;

        const agentEntries = Object.entries(agents);
        
        if (agentEntries.length === 0) {
            agentsContainer.innerHTML = `
                <div class="loading">
                    🔍 No agents discovered yet...
                </div>
            `;
            return;
        }

        const agentsHtml = agentEntries.map(([agentId, agent]) => {
            const isMalicious = agent.threat_analysis?.is_malicious || false;
            const statusClass = agent.status === 'active' ? 'status-active' : 
                               isMalicious ? 'status-critical' : 'status-inactive';
            const badgeClass = agent.status === 'active' ? 'badge-active' : 'badge-inactive';
            const threatBadgeClass = isMalicious ? 'badge-critical' : 'badge-low';
            const threatLevel = isMalicious ? 'CRITICAL' : 'LOW';

            return `
                <div class="agent-item ${isMalicious ? 'critical-alert' : ''}">
                    <div class="agent-status ${statusClass} ${isMalicious ? 'pulse' : ''}"></div>
                    <div class="agent-info">
                        <div class="agent-name">${agent.name || 'Unknown Agent'}</div>
                        <div class="agent-details">🔗 Port: ${agent.port} • 👁 Last seen: ${agent.last_seen || 'Unknown'}</div>
                    </div>
                    <div class="agent-badge ${badgeClass}">${(agent.status || 'unknown').toUpperCase()}</div>
                    <div class="agent-badge ${threatBadgeClass}">${threatLevel}</div>
                </div>
            `;
        }).join('');

        const totalSection = `
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #374151;">
                <div class="stat-item">
                    <span class="stat-label">Total Agents</span>
                    <span class="stat-value">${agentEntries.length}</span>
                </div>
            </div>
        `;

        agentsContainer.innerHTML = agentsHtml + totalSection;
    }

    updateSecurityStatus(data) {
        // Update Security Status block in real-time
        this.updateElement('security-events-count', data.security_events?.length || 0);
        this.updateElement('threat-level', data.threat_level || 'LOW', `value-${this.getThreatLevelClass(data.threat_level)}`);
        this.updateElement('malicious-count', data.malicious_count || 0, data.malicious_count > 0 ? 'value-critical' : 'value-success');
        this.updateElement('overall-score', `${data.overall_score || 0}/100`, this.getScoreClass(data.overall_score));
        
        // Update last scan time
        this.updateElement('last-scan', 'Just now', 'value-info');
    }

    updateCriticalAlert(criticalAlert) {
        // Find the critical alert card and update it
        const alertCards = document.querySelectorAll('.card');
        let criticalAlertCard = null;
        
        // Find the card with "Critical Alert" or "System Status" title
        alertCards.forEach(card => {
            const title = card.querySelector('.card-title');
            if (title && (title.textContent.includes('Critical Alert') || title.textContent.includes('System Status'))) {
                criticalAlertCard = card;
            }
        });

        if (!criticalAlertCard) return;

        if (criticalAlert) {
            // Show critical alert
            criticalAlertCard.className = 'card critical-alert';
            criticalAlertCard.innerHTML = `
                <div class="card-title">
                    <span class="card-title-icon">⚠️</span>
                    Critical Alert
                </div>
                
                <div style="text-align: center; padding: 1rem 0;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚨</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #ef4444; margin-bottom: 0.5rem;">
                        HOSTILE AGENT ACTIVE
                    </div>
                    <div style="font-size: 0.9rem; color: #fca5a5; margin-bottom: 1rem;">
                        ${criticalAlert.agent_name} exhibiting malicious behavior
                    </div>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">🔗 Port</span>
                    <span class="stat-value">${criticalAlert.port}</span>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">⚠️ Threat Score</span>
                    <span class="stat-value value-critical">${criticalAlert.threat_score}/100</span>
                </div>
                
                <div class="stat-item">
                    <span class="stat-label">🛡️ Security Alerts</span>
                    <span class="stat-value">
                        <div style="font-size: 0.8rem; color: #fca5a5;">
                            ${criticalAlert.alerts.map(alert => `• ${alert}`).join('<br>')}
                        </div>
                    </span>
                </div>
            `;
        } else {
            // Show all clear
            criticalAlertCard.className = 'card';
            criticalAlertCard.innerHTML = `
                <div class="card-title">
                    <span class="card-title-icon">✅</span>
                    System Status
                </div>
                
                <div style="text-align: center; padding: 2rem 0;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #22c55e; margin-bottom: 0.5rem;">
                        ALL SYSTEMS SECURE
                    </div>
                    <div style="font-size: 0.9rem; color: #94a3b8;">
                        No critical threats detected
                    </div>
                </div>
            `;
        }
    }

    updateTentacleMatrix(tentacleScores) {
        const matrixContainer = document.querySelector('.tentacle-matrix');
        if (!matrixContainer || !tentacleScores.length) return;

        const matrixHtml = tentacleScores.map(tentacle => `
            <div class="tentacle-item">
                <div class="tentacle-number">${tentacle.id}</div>
                <div class="tentacle-name">${tentacle.name}</div>
                <div class="tentacle-score ${this.getScoreClass(tentacle.score)}">${tentacle.score}</div>
            </div>
        `).join('');

        matrixContainer.innerHTML = matrixHtml;
    }

    updateRecentEvents(events) {
        const eventsContainer = document.getElementById('recent-events');
        if (!eventsContainer) return;

        if (!events || events.length === 0) {
            eventsContainer.innerHTML = `
                <div class="recent-event event-info">
                    <div class="event-icon">✅</div>
                    <div class="event-content">
                        <div class="event-title">ALL CLEAR</div>
                        <div class="event-description">No security events detected</div>
                        <div class="event-time">🕐 System monitoring active</div>
                    </div>
                </div>
            `;
            return;
        }

        const recentEvents = events.slice(0, 3);
        const eventsHtml = recentEvents.map(event => {
            const isCritical = event.type === 'malicious_agent_detected' || event.severity === 'critical';
            const icon = isCritical ? '🚨' : '🔍';
            const eventClass = isCritical ? 'event-critical' : 'event-info';
            
            return `
                <div class="recent-event ${eventClass}">
                    <div class="event-icon">${icon}</div>
                    <div class="event-content">
                        <div class="event-title">${(event.type || 'unknown').replace(/_/g, ' ').toUpperCase()}</div>
                        <div class="event-description">${event.description || 'No description available'}</div>
                        <div class="event-time">🕐 ${this.formatTimestamp(event.timestamp)}</div>
                    </div>
                </div>
            `;
        }).join('');

        eventsContainer.innerHTML = eventsHtml;
    }

    updateIntelligenceOverview(data) {
        this.updateElement('active-connections-count', data.active_connections || 0);
        this.updateElement('messages-intercepted-count', data.messages_intercepted || 0);
        this.updateElement('avg-response-time', `${data.avg_response_time || 0}ms`);
    }

    updateElement(id, value, className = '') {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            if (className) {
                element.className = `stat-value ${className}`;
            }
        }
    }

    getThreatLevelClass(threatLevel) {
        switch (threatLevel?.toLowerCase()) {
            case 'critical': return 'critical';
            case 'high': return 'warning';
            case 'medium': return 'warning';
            case 'low': return 'success';
            default: return 'success';
        }
    }

    getScoreClass(score) {
        if (score >= 80) return 'score-high';
        if (score >= 60) return 'score-medium';
        return 'score-low';
    }

    formatTimestamp(timestamp) {
        if (!timestamp) return 'Unknown';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString();
        } catch (error) {
            return 'Invalid time';
        }
    }

    setupEventListeners() {
        // Enhanced keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key) {
                    case 'r':
                        event.preventDefault();
                        this.refreshDashboard();
                        this.showNotification('Dashboard refreshed manually', 'info');
                        break;
                }
            }
        });

        // Page visibility API for smart updates
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('⏸️ Dashboard hidden, reducing update frequency');
            } else {
                console.log('▶️ Dashboard visible, resuming full updates');
                this.refreshDashboard(); // Immediate refresh when page becomes visible
            }
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const colors = {
            info: '#3b82f6',
            warning: '#f59e0b',
            critical: '#ef4444',
            success: '#22c55e'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1e293b;
            border: 1px solid ${colors[type] || colors.info};
            border-radius: 0.5rem;
            padding: 1rem;
            color: #e2e8f0;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    showError(message) {
        this.showNotification(message, 'critical');
        console.error('Dashboard error:', message);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.inktraceDashboard = new InktraceDashboard();
    console.log('🐙 Enhanced Inktrace Dashboard initialized with real-time threat detection');
});

// Add enhanced CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification-critical {
        border-color: #ef4444 !important;
        background: linear-gradient(135deg, #1f2937 0%, #7f1d1d 100%) !important;
    }
    
    .notification-warning {
        border-color: #f59e0b !important;
        background: linear-gradient(135deg, #1f2937 0%, #78350f 100%) !important;
    }
    
    .notification-success {
        border-color: #22c55e !important;
        background: linear-gradient(135deg, #1f2937 0%, #14532d 100%) !important;
    }
    
    /* Enhanced real-time update indicators */
    .updating {
        animation: glow 1s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 5px rgba(96, 165, 250, 0.5); }
        to { box-shadow: 0 0 20px rgba(96, 165, 250, 0.8); }
    }
`;
document.head.appendChild(style);