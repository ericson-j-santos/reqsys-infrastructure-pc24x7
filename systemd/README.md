# ReqSys PC24x7 — Systemd Units

Automatic restart of Docker Compose stacks after power loss or system reboot.

## Prerequisites

- Linux with systemd (or WSL2 Ubuntu with systemd enabled)
- Docker + Docker Compose v2.x+
- Git clone of ReqSys in `/home/reqsys-admin/reqsys-{dev,hml,prod}`

## Installation

### 1. Customize for your environment

Edit the paths and ports in each `.service` file to match your setup:

```bash
# Example for dev environment at /home/reqsys-admin/reqsys-dev
cat systemd/reqsys-dev.service
# Update: WorkingDirectory, BACKEND_PORT, POSTGRES_PORT, GATEWAY_PORT
```

### 2. Copy to systemd

```bash
sudo cp systemd/reqsys-dev.service /etc/systemd/system/
sudo cp systemd/reqsys-hml.service /etc/systemd/system/
sudo cp systemd/reqsys-prod.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### 3. Enable and start

```bash
# Enable auto-start on boot
sudo systemctl enable reqsys-dev.service
sudo systemctl enable reqsys-hml.service
sudo systemctl enable reqsys-prod.service

# Start now
sudo systemctl start reqsys-dev.service
sudo systemctl start reqsys-hml.service
sudo systemctl start reqsys-prod.service
```

## Verification

```bash
# Check status
systemctl status reqsys-dev.service
systemctl status reqsys-hml.service
systemctl status reqsys-prod.service

# View logs
sudo journalctl -u reqsys-dev.service -f
sudo journalctl -u reqsys-hml.service -f
sudo journalctl -u reqsys-prod.service -f

# Verify containers are running
docker ps | grep reqsys
```

## Testing

Test restart behavior:

```bash
# Stop a container
docker-compose -f /home/reqsys-admin/reqsys-dev/docker-compose.yml \
                -f /home/reqsys-admin/reqsys-dev/docker-compose.dev.yml down

# Systemd will restart it within RestartSec (10-15 seconds)
sleep 20
docker ps | grep reqsys-dev  # should show running containers
```

## Stopping services

```bash
sudo systemctl stop reqsys-dev.service
sudo systemctl stop reqsys-hml.service
sudo systemctl stop reqsys-prod.service
```

## Disabling auto-start

```bash
sudo systemctl disable reqsys-dev.service
sudo systemctl disable reqsys-hml.service
sudo systemctl disable reqsys-prod.service
```

## Environment Variables

Each service file sets:

- `COMPOSE_PROJECT_NAME`: isolates containers by environment
- `BACKEND_PORT_*`: API port (8210/8211/8212 by default)
- `POSTGRES_PORT_*`: Database port (5432/5433/5434 by default)
- `GATEWAY_PORT_*`: Nginx gateway port (8081/8082/8083 by default)

Adjust these in the `.service` files before installing.

## Troubleshooting

### Service fails to start

```bash
# Check logs
sudo journalctl -u reqsys-dev.service -n 50

# Verify working directory exists
ls -la /home/reqsys-admin/reqsys-dev/

# Test docker-compose manually
cd /home/reqsys-admin/reqsys-dev
docker-compose -f docker-compose.yml -f docker-compose.dev.yml config
```

### Docker daemon not starting

```bash
# Ensure docker.service is enabled
sudo systemctl enable docker.service
sudo systemctl start docker.service

# Check docker status
systemctl status docker.service
```

### Permission denied errors

```bash
# Ensure docker group includes your user (if not using sudo)
sudo usermod -aG docker $USER
newgrp docker  # apply group changes
```

## Notes

- Type=oneshot with RemainAfterExit=yes means the service stays "active" even when no process is running
- Restart=on-failure ensures automatic restart on crash
- RestartSec delays restart attempt (good for catching transient errors)
- Dependencies are tracked with After/Requires to ensure docker starts first
