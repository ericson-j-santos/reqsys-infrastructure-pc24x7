# ReqSys Infrastructure — PC24x7

Generic infrastructure-as-code for hosting ReqSys (or any Docker Compose application) on a 24x7 PC using:

- **Docker Compose** for app orchestration
- **Cloudflare Tunnel** for public exposure (without port forwarding)
- **Restic + Cloudflare R2** for encrypted backup
- **Systemd** for automatic restart after power loss

**This repo is infrastructure-independent** — configure once, deploy ReqSys, ReqSys 2.0, or any Compose-based app.

## Quick Start

1. Clone ReqSys repository to `/home/reqsys-admin/reqsys-{dev,hml,prod}` on your 24x7 PC
2. Customize `systemd/reqsys-*.service` files with your paths and ports
3. Copy services to `/etc/systemd/system/` and enable them
4. Install Cloudflare Tunnel and restic for backup
5. Deploy

See [docs/setup-linux.md](docs/setup-linux.md) for step-by-step guide.

## Repository Structure

```
systemd/
  ├── README.md                      — Installation & troubleshooting
  ├── reqsys.service.template        — Generic template
  ├── reqsys-dev.service             — Dev environment
  ├── reqsys-hml.service             — Staging environment
  └── reqsys-prod.service            — Production environment

docs/
  ├── setup-linux.md                 — Full setup guide (Linux)
  ├── setup-wsl2.md                  — Setup for WSL2 + Ubuntu
  ├── cloudflare-tunnel.md           — Quick Tunnel & named tunnels
  └── backup-restore.md              — Restic + R2 backup/restore

scripts/
  ├── health-check.sh                — Health endpoint monitor
  ├── monitor.sh                     — System monitoring (CPU, disk, uptime)
  └── install-services.sh            — Automated install

.github/workflows/
  ├── deploy-pc24x7-dev.yml          — Auto-deploy on push to main
  ├── deploy-pc24x7-hml.yml          — Manual deploy with approval
  └── deploy-pc24x7-prod.yml         — Manual deploy + backup validation
```

## Key Features

### Automatic Restart

Systemd units ensure Docker Compose stacks restart after:
- Power loss (requires BIOS auto-power-on setting)
- System reboot
- Docker daemon crash

### Public Exposure (No port forwarding)

Cloudflare Tunnel (`cloudflared`) handles:
- Inbound connections from internet → PC on local network
- No need to open ports on router
- No IP address exposure
- Free (up to 50 concurrent connections per app)

### Backup & Restore

Restic + Cloudflare R2 (10 GiB free):
- Encrypted backups (AES-256-GCM)
- Automated retention policies (14/30/90 days by environment)
- Restore to any point-in-time

### CI/CD Workflows

Three GitHub Actions workflows for deploy:

1. **dev**: Auto-deploy on every push to `main`
   - No approval needed
   - Smoke test on health endpoint
   
2. **hml**: Manual dispatch workflow
   - Requires approval in GitHub environment
   - Pre-deploy backup
   
3. **prod**: Manual dispatch + backup validation
   - Gate: GitHub environment approval
   - Pre-flight: R2 bucket + restic repository checks
   - Pre-deploy backup mandatory

## Cost (Phase 1)

| Item | Cost |
|------|------|
| PC 24x7 (electricity) | ~R$30–80/month |
| Cloudflare Tunnel | Free (plan: Free) |
| Backup (R2 + restic) | Free (10 GiB) |
| **Total Phase 1** | **Electricity only** |

## Cost (Phase 2 — optional domain)

| Item | Cost |
|------|------|
| Domain (registrar) | ~R$40–60/year |
| Cloudflare DNS | Free (plan: Free) |
| Named Tunnel | Free (plan: Free) |
| **Additional Phase 2** | **~R$3–5/month** |

## Prerequisites

### Hardware

- PC with 4+ CPU cores, 4GB+ RAM, 100GB+ disk
- 24x7 power supply (with UPS recommended)
- Stable internet connection (cable/fiber preferred)

### Software

- Linux (Ubuntu 20.04+ recommended) OR WSL2 + Ubuntu
- Docker Engine 20.10+
- Docker Compose v2.0+
- `cloudflared` CLI
- `restic` for backups
- `curl`, `jq` for health checks

### Credentials / Secrets

```bash
# Cloudflare
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_API_TOKEN=xxx

# R2 (S3-compatible)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
RESTIC_PASSWORD=xxx
RESTIC_REPOSITORY=s3:https://...
```

## Setup (30 minutes)

```bash
# 1. Install Docker, cloudflared, restic, curl, jq
sudo apt update && sudo apt install -y docker.io docker-compose curl jq
# ... (see docs/setup-linux.md for cloudflared + restic)

# 2. Clone ReqSys
cd /home/reqsys-admin
git clone https://github.com/your-org/reqsys-v2-enterprise-real.git reqsys-dev
cd reqsys-dev
cp .env.example .env
# Edit .env with your secrets

# 3. Copy systemd units
sudo cp ../reqsys-infrastructure-pc24x7/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable reqsys-dev.service
sudo systemctl start reqsys-dev.service

# 4. Expose via Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8081

# 5. Setup backup (automated later)
cd /home/reqsys-admin/reqsys-dev
./scripts/pc24x7_backup_restic.sh dev
```

## Validation Checklist (before marking production-ready)

- [ ] Service starts after reboot
- [ ] Health endpoint responds consistently
- [ ] Backup runs without errors (check `restic snapshots`)
- [ ] Restore from backup successful (test restore locally)
- [ ] Cloudflare Tunnel stays connected 7+ days
- [ ] CPU/memory/disk usage acceptable
- [ ] CI/CD workflow deploys successfully

## Troubleshooting

See [systemd/README.md](systemd/README.md) for systemd issues.

See [docs/](docs/) for Cloudflare Tunnel and backup troubleshooting.

## Development / Customization

### For a different app

1. Create new `docker-compose.yml` (or use existing)
2. Customize `systemd/*.service`:
   - `WorkingDirectory` → your app path
   - `ExecStart` → your docker-compose command
3. Adjust `BACKEND_PORT`, `POSTGRES_PORT`, `GATEWAY_PORT` as needed

### For a different PC setup

1. WSL2? See [docs/setup-wsl2.md](docs/setup-wsl2.md)
2. Different paths? Edit `.service` files before installing
3. Different ports? Update `GATEWAY_PORT_*` in `.service`

## Documentation

- [Systemd Units](systemd/README.md) — Installation, testing, troubleshooting
- [Linux Setup](docs/setup-linux.md) — Complete step-by-step guide
- [WSL2 Setup](docs/setup-wsl2.md) — Windows Subsystem for Linux 2
- [Cloudflare Tunnel](docs/cloudflare-tunnel.md) — Quick Tunnel vs. named tunnels
- [Backup & Restore](docs/backup-restore.md) — Restic + R2 operations

## Related

- [ReqSys Repository](https://github.com/ericson-j-santos/reqsys-v2-enterprise-real) — Main app
- [ADR-046 — PC24x7](https://github.com/ericson-j-santos/reqsys-v2-enterprise-real/blob/main/docs/ADR/ADR-046-pc24x7-substituicao-flyio.md) — Architecture Decision Record
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
- [Restic Documentation](https://restic.readthedocs.io/)

## License

Same as ReqSys repository.

## Support

For ReqSys-specific issues → check ReqSys repo  
For PC24x7 infrastructure issues → open issue here
