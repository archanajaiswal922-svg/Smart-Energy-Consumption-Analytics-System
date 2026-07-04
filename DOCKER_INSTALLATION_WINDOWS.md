# Docker Installation & Setup Guide - Windows

## Quick Installation Steps

### Option 1: Docker Desktop (Recommended for Windows 10/11)

1. **Download Docker Desktop for Windows**
   - Visit: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"
   - Download the installer (Docker Desktop Installer.exe)

2. **Install Docker Desktop**
   ```
   - Double-click the installer
   - Follow the installation wizard
   - Choose: "WSL 2" (Windows Subsystem for Linux 2) option if prompted
   - Restart your computer when prompted
   ```

3. **Enable WSL 2 (if not already enabled)**
   ```powershell
   # Open PowerShell as Administrator and run:
   wsl --install
   wsl --set-default-version 2
   ```

4. **Verify Installation**
   ```powershell
   docker --version
   docker run hello-world
   ```

### Option 2: Docker on Windows 11 via Windows Package Manager

```powershell
# Open PowerShell as Administrator
winget install Docker.DockerDesktop
```

### Option 3: Docker via Chocolatey

```powershell
# Install Chocolatey first if you don't have it
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Docker
choco install docker-desktop
```

## After Installation

### 1. Start Docker Desktop
- Find "Docker Desktop" in the Start Menu
- Launch it (it will start Docker daemon)
- Wait for "Docker is running" notification in system tray

### 2. Verify Installation
```powershell
docker --version
docker ps
```

### 3. Build the Spark Application
```powershell
cd "c:\Users\Archana Jaiswal\OneDrive\Desktop\AI_COMPUTE_CASE_STUDY_7"
docker build -t smart-energy-analytics:latest .
```

### 4. Run the Application
```powershell
mkdir output, logs
docker run --rm `
  -v "$((Get-Location))\powerconsumption.csv:/data/powerconsumption.csv:ro" `
  -v "$((Get-Location))\output:/output" `
  -v "$((Get-Location))\logs:/spark/logs" `
  smart-energy-analytics:latest
```

## Windows System Requirements

- **Operating System**: Windows 10 (Build 19041+) or Windows 11
- **Processor**: 2+ cores with virtualization support
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk Space**: 20GB+ for Docker images
- **Virtualization**: Enabled in BIOS

### Check Virtualization Support

```powershell
# Run in PowerShell as Administrator
Get-ComputerInfo | Select-Object HyperVisorPresent, CsProcessors
```

## Troubleshooting

### Problem: "Cannot connect to Docker daemon"
**Solution**: 
1. Start Docker Desktop from Start Menu
2. Wait for it to fully initialize (check system tray)
3. Run `docker ps` to verify

### Problem: "Docker not found" after installation
**Solution**:
1. Restart PowerShell
2. Or restart your computer
3. Ensure Docker Desktop is running

### Problem: Insufficient disk space
**Solution**:
```powershell
# Clean up Docker resources
docker system prune -a --volumes
```

### Problem: WSL 2 issues
**Solution**:
1. Open PowerShell as Administrator
2. Run: `wsl --install --verbose`
3. Restart computer
4. Restart Docker Desktop

## System Resources

### Check Available Resources
```powershell
Get-ComputerInfo | Select-Object CsSystemType, CsProcessors, @{
    Name="RAM_GB"
    Expression={[math]::Round($_.CsPhyicallyInstalledSystemMemory/1MB, 2)}
}
```

### Allocate Resources to Docker Desktop
1. Open Docker Desktop Settings (right-click tray icon → Settings)
2. Go to Resources → Advanced
3. Set:
   - CPUs: 4 (or more)
   - Memory: 4GB-6GB
   - Swap: 1GB
4. Apply & Restart

## Quick Build & Test After Installation

Once Docker is installed and running:

```powershell
# 1. Build the image
docker build -t smart-energy-analytics:latest .

# 2. Create output directories
mkdir output, logs

# 3. Run the container
docker run --rm `
  -v "$((Get-Location))\powerconsumption.csv:/data/powerconsumption.csv:ro" `
  -v "$((Get-Location))\output:/output" `
  -v "$((Get-Location))\logs:/spark/logs" `
  -e INPUT_DATA=/data/powerconsumption.csv `
  -e OUTPUT_DIR=/output/results `
  smart-energy-analytics:latest

# 4. Check results
dir output/results
```

## Docker Desktop Usage Tips

### Start Docker on System Boot
1. Open Docker Desktop Settings
2. Go to General tab
3. Enable "Start Docker Desktop when you log in"

### Monitor Resource Usage
- Right-click Docker icon in system tray
- Select "Dashboard"
- View containers, images, and resource usage

### View Container Logs
```powershell
# List running containers
docker ps

# View logs of a container
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

## Next Steps

1. **Install Docker Desktop**: Follow Option 1 above
2. **Restart your computer** (important!)
3. **Navigate to project folder**:
   ```powershell
   cd "c:\Users\Archana Jaiswal\OneDrive\Desktop\AI_COMPUTE_CASE_STUDY_7"
   ```
4. **Build the image**:
   ```powershell
   docker build -t smart-energy-analytics:latest .
   ```
5. **Run the application**:
   ```powershell
   mkdir output, logs
   docker run --rm -v "$((Get-Location))\powerconsumption.csv:/data/powerconsumption.csv:ro" -v "$((Get-Location))\output:/output" smart-energy-analytics:latest
   ```

## Useful Resources

- **Docker Download**: https://www.docker.com/products/docker-desktop
- **Docker Documentation**: https://docs.docker.com/
- **Docker for Windows Guide**: https://docs.docker.com/desktop/install/windows-install/
- **WSL 2 Setup**: https://docs.microsoft.com/en-us/windows/wsl/install-win10

---

**Estimated Installation Time**: 15-20 minutes
**Restart Required**: Yes (after installation)
**Status**: Ready to proceed after Docker installation
