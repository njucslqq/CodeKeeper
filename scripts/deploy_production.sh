#!/bin/bash

# Production deployment script for Git Deep Analyzer
# This script automates the deployment process

set -e

echo "=================================="
echo "  Git Deep Analyzer - Production Deployment"
echo "=================================="
echo ""

# Configuration
INSTALL_DIR="/opt/git-deep-analyzer"
SERVICE_USER="gitanalyzer"
SERVICE_GROUP="gitanalyzer"
VENV_DIR="${INSTALL_DIR}/venv"
REPO_URL="git@github.com:njucslqq/CodeKeeper.git"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}ERROR: This script must be run as root${NC}"
    echo "Use: sudo $0"
    exit 1
fi

# Parse arguments
FORCE_INSTALL=${1:-0}
SKIP_VENV=${1:-0}

# Function: print info
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function: print warning
warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function: print error
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Install system dependencies
echo "Step 1: Installing system dependencies"
echo "---"

if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git
elif command -v yum &> /dev/null; then
    # RHEL/CentOS
    yum install -y python3 python3-pip python3-venv git
elif command -v brew &> /dev/null; then
    # macOS
    brew install python3
else
    info "No package manager found, skipping system dependencies installation"
fi

# Step 2: Create service user
echo ""
echo "Step 2: Creating service user"
echo "---"

if ! id "$SERVICE_USER" &> /dev/null; then
    useradd -m -s /bin/bash "$SERVICE_USER"
    info "Created user: $SERVICE_USER"
else
    info "User $SERVICE_USER already exists"
fi

# Step 3: Clone or update repository
echo ""
echo "Step 3: Installing/updating repository"
echo "---"

if [ -d "$INSTALL_DIR" ]; then
    if [ "$FORCE_INSTALL" = "0" ]; then
        warn "Installation directory already exists. Use --force to reinstall."
        read -p "Continue anyway? (y/N) " -n 1
        [[ $REPLY =~ ^[Yy] ]] || exit 0
    fi
    cd "$INSTALL_DIR"
    info "Updating repository..."
    git fetch origin
    git reset --hard origin/main || true
else
    info "Creating installation directory..."
    mkdir -p "$INSTALL_DIR"
    chown "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    chmod 755 "$INSTALL_DIR"

    info "Cloning repository..."
    sudo -u "$SERVICE_USER" git clone "$REPO_URL" "$INSTALL_DIR"
fi

chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"

# Step 4: Install Python dependencies
echo ""
echo "Step 4: Installing Python dependencies"
echo "---"

cd "$INSTALL_DIR"

# Create virtual environment if it doesn't exist
if [ "$SKIP_VENV" = "0" ]; then
    if [ ! -d "$VENV_DIR" ]; then
        info "Creating virtual environment..."
        sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"
    fi
else
    info "Virtual environment already exists (use --skip-venv to recreate)"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
info "Installing dependencies..."
pip install --quiet -e ".[cpp]" || {
    error "Failed to install dependencies"
    exit 1
}

# Step 5: Create configuration directory
echo ""
echo "Step 5: Creating configuration directories"
echo "---"

CONFIG_DIR="/etc/${SERVICE_USER}"
mkdir -p "$CONFIG_DIR"

# Create environment file
ENV_FILE="$CONFIG_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    info "Creating environment file: $ENV_FILE"
    cat > "$ENV_FILE" << 'EOF'
# Git Deep Analyzer Environment Configuration
# Copy this file to .git-deep-analyzer.yaml for configuration

# AI API Keys
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=

# External System Tokens
# JIRA_TOKEN=
# CONFLUENCE_TOKEN=
# FEISHU_USER_ACCESS_TOKEN=

# Service Configuration
# GDA_CONFIG=/etc/gitanalyzer/.git-deep-analyzer.yaml
# GDA_LOGS=/var/log/gitanalyzer
EOF
    chown "$SERVICE_USER:$SERVICE_GROUP" "$ENV_FILE"
    chmod 640 "$ENV_FILE"
else
    info "Environment file already exists: $ENV_FILE"
fi

# Step 6: Create log directory
echo ""
echo "Step 6: Creating log directory"
echo "---"

LOG_DIR="/var/log/${SERVICE_USER}"
mkdir -p "$LOG_DIR"
chown "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Step 7: Create systemd service file
echo ""
echo "Step 7: Creating systemd service"
echo "---"

SERVICE_FILE="/etc/systemd/system/${SERVICE_USER}.service"

cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Git Deep Analyzer
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$CONFIG_DIR/.env
ExecStart=$VENV_DIR/bin/git-deep-analyze analyze
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

info "Service file created: $SERVICE_FILE"

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable gitanalyzer

# Step 8: Create systemd timer service (optional)
echo ""
echo "Step 8: Creating systemd timer service (for scheduled runs)"
echo "---"

TIMER_FILE="/etc/systemd/system/${SERVICE_USER}.timer"

cat > "$TIMER_FILE" << 'EOF'
[Unit]
Description=Run Git Deep Analyzer daily

[Timer]
OnCalendar=daily
Persistent=true

[Service]
Type=oneshot
User=$SERVICE_USER
EnvironmentFile=$CONFIG_DIR/.env
ExecStart=$VENV_DIR/bin/git-deep-analyze analyze
EOF

systemctl daemon-reload
systemctl enable gitanalyzer.timer

# Step 9: Set up log rotation
echo ""
echo "Step 9: Setting up log rotation"
echo "---"

ROTATE_CONF="/etc/logrotate.d/${SERVICE_USER}"
cat > "$ROTATE_CONF" << 'EOF'
/var/log/${SERVICE_USER}/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640
    sharedscripts
    postrotate
    extension
}
EOF

info "Log rotation configured: $ROTATE_CONF"

# Step 10: Test installation
echo ""
echo "Step 10: Testing installation"
echo "---"

# Test import
info "Testing Python import..."
sudo -u "$SERVICE_USER" python3 -c "
import sys
try:
    import git_deep_analyzer
    print('OK')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    error "Python import test failed"
    exit 1
fi

# Final summary
echo ""
echo "=================================="
echo "  Deployment Complete!"
echo "=================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "Virtual environment: $VENV_DIR"
echo "Configuration directory: $CONFIG_DIR"
echo "Log directory: $LOG_DIR"
echo ""
echo "Next steps:"
echo "1. Edit configuration: $CONFIG_DIR/.git-deep-analyzer.yaml"
echo "2. Start service: sudo systemctl start gitanalyzer"
echo "3. Check status: sudo systemctl status gitanalyzer"
echo "4. View logs: sudo journalctl -u gitanalyzer -f"
echo ""
echo "Service management commands:"
echo "  Start:   sudo systemctl start gitanalyzer"
echo "  Stop:    sudo systemctl stop gitanalyzer"
echo "  Restart:  sudo systemctl restart gitanalyzer"
echo "  Status:  sudo systemctl status gitanalyzer"
echo "  Logs:    sudo journalctl -u gitanalyzer -f"
echo ""
info "Deployment completed successfully!"
