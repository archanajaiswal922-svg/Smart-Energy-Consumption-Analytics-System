# Smart Energy Analytics - Docker Build & Test Script (PowerShell)
# Windows-compatible build automation

param(
    [switch]$SkipBuild = $false,
    [switch]$SkipTest = $false,
    [string]$ImageName = "smart-energy-analytics",
    [string]$ImageTag = "latest"
)

# Configuration
$IMAGE = "$ImageName`:$ImageTag"
$OUTPUT_DIR = "output"
$LOGS_DIR = "logs"
$TEST_RESULTS = "test_results.txt"

# Color output
$ColorGreen = 'Green'
$ColorRed = 'Red'
$ColorYellow = 'Yellow'
$ColorBlue = 'Cyan'

# Functions
function Write-Header {
    param([string]$Text)
    Write-Host "`n========================================" -ForegroundColor $ColorBlue
    Write-Host $Text -ForegroundColor $ColorBlue
    Write-Host "========================================`n" -ForegroundColor $ColorBlue
}

function Write-Test {
    param([string]$Text)
    Write-Host "[TEST] $Text" -ForegroundColor $ColorYellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "[PASS] $Text" -ForegroundColor $ColorGreen
}

function Write-Error {
    param([string]$Text)
    Write-Host "[FAIL] $Text" -ForegroundColor $ColorRed
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor $ColorBlue
}

# Test 1: Docker Installation
function Test-DockerInstallation {
    Write-Test "Docker installation"
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        $version = & docker --version
        Write-Success "Docker is installed: $version"
        return $true
    } else {
        Write-Error "Docker is not installed"
        Write-Info "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
        return $false
    }
}

# Test 2: Docker Daemon
function Test-DockerDaemon {
    Write-Test "Docker daemon connectivity"
    try {
        $info = & docker info 2>$null
        Write-Success "Docker daemon is running"
        return $true
    } catch {
        Write-Error "Cannot connect to Docker daemon"
        Write-Info "Please start Docker Desktop"
        return $false
    }
}

# Test 3: Input Data
function Test-InputData {
    Write-Test "Checking input data"
    if (Test-Path "powerconsumption.csv") {
        $fileSize = (Get-Item "powerconsumption.csv").Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        Write-Success "Input data found: $fileSizeMB MB"
        return $true
    } else {
        Write-Error "Input data file not found: powerconsumption.csv"
        return $false
    }
}

# Test 4: Build Docker Image
function Test-BuildImage {
    Write-Test "Building Docker image"
    
    if ($SkipBuild) {
        Write-Info "Skipping build (--SkipBuild flag set)"
        return $true
    }
    
    Write-Info "Starting build... this may take several minutes"
    
    try {
        $output = & docker build -t $IMAGE . 2>&1
        
        # Check if build was successful
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker image built successfully"
            Write-Info "Image: $IMAGE"
            return $true
        } else {
            Write-Error "Failed to build Docker image"
            Write-Error "Build output:`n$output"
            return $false
        }
    } catch {
        Write-Error "Build failed: $_"
        return $false
    }
}

# Test 5: Image Verification
function Test-ImageExists {
    Write-Test "Verifying image exists"
    try {
        $images = & docker images --filter "reference=$IMAGE" --format "{{.Size}}"
        if ($images) {
            $imageSize = $images[0]
            Write-Success "Image exists with size: $imageSize"
            return $true
        } else {
            Write-Error "Image not found"
            return $false
        }
    } catch {
        Write-Error "Failed to verify image: $_"
        return $false
    }
}

# Test 6: Create Output Directories
function Test-CreateDirectories {
    Write-Test "Creating output directories"
    try {
        if (-not (Test-Path $OUTPUT_DIR)) {
            New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null
        }
        if (-not (Test-Path $LOGS_DIR)) {
            New-Item -ItemType Directory -Path $LOGS_DIR | Out-Null
        }
        Write-Success "Output directories created"
        return $true
    } catch {
        Write-Error "Failed to create directories: $_"
        return $false
    }
}

# Test 7: Run Container
function Test-RunContainer {
    Write-Test "Running container - execution test"
    
    if ($SkipTest) {
        Write-Info "Skipping test execution (--SkipTest flag set)"
        return $true
    }
    
    Write-Info "Starting container... please wait"
    
    try {
        $containerOutput = @()
        $cwd = (Get-Location).Path
        
        # Build the docker run command
        $inputPath = Join-Path $cwd 'powerconsumption.csv'
        $outputPath = Join-Path $cwd $OUTPUT_DIR
        $logsPath = Join-Path $cwd $LOGS_DIR
        $inputVolume = "$inputPath:/data/powerconsumption.csv:ro"
        $outputVolume = "$outputPath:/output"
        $logsVolume = "$logsPath:/spark/logs"
        $runCmd = @(
            "docker", "run", "--rm",
            "-v", $inputVolume,
            "-v", $outputVolume,
            "-v", $logsVolume,
            "-e", "INPUT_DATA=/data/powerconsumption.csv",
            "-e", "OUTPUT_DIR=/output/results",
            $IMAGE
        )
        
        # Run the container
        & docker run --rm `
            -v "$inputVolume" `
            -v "$outputVolume" `
            -v "$logsVolume" `
            -e INPUT_DATA=/data/powerconsumption.csv `
            -e OUTPUT_DIR=/output/results `
            $IMAGE 2>&1 | Tee-Object -FilePath $TEST_RESULTS
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Container executed successfully"
            return $true
        } else {
            Write-Error "Container execution failed"
            return $false
        }
    } catch {
        Write-Error "Failed to run container: $_"
        return $false
    }
}

# Test 8: Verify Output Files
function Test-OutputFiles {
    Write-Test "Verifying output files"
    
    $resultsPath = Join-Path $OUTPUT_DIR "results"
    
    if (Test-Path $resultsPath) {
        $csvFiles = Get-ChildItem -Path $resultsPath -Filter "*.csv" | Measure-Object
        $fileCount = $csvFiles.Count
        
        if ($fileCount -gt 0) {
            Write-Success "Output files generated: $fileCount CSV file(s)"
            
            # Show file details
            $csvFiles.Name | ForEach-Object {
                $filePath = Join-Path $resultsPath $_
                $fileSize = (Get-Item $filePath).Length
                $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
                Write-Info ("  - " + $_ + ": " + $fileSizeMB + " MB")
            }
            return $true
        } else {
            Write-Error "No output CSV files found"
            return $false
        }
    } else {
        Write-Error "Output directory not created: $resultsPath"
        return $false
    }
}

# Main execution
function Main {
    Write-Header "Smart Energy Analytics - Docker Build & Test"
    
    # Clear previous test results
    if (Test-Path $TEST_RESULTS) {
        Remove-Item $TEST_RESULTS -Force
    }
    
    # Track test results
    [int]$testsPass = 0
    [int]$testsFail = 0
    
    # Run tests
    $tests = @(
        { Test-DockerInstallation },
        { Test-DockerDaemon },
        { Test-InputData },
        { Test-CreateDirectories },
        { Test-BuildImage },
        { Test-ImageExists },
        { Test-RunContainer },
        { Test-OutputFiles }
    )
    
    $testResults = @()
    foreach ($test in $tests) {
        $result = & $test
        $testResults += $result
        if ($result) { $testsPass++ } else { $testsFail++ }
    }
    
    # Print summary
    Write-Header "Test Summary"
    Write-Host "Total Passed: $testsPass" -ForegroundColor $ColorGreen
    Write-Host "Total Failed: $testsFail" -ForegroundColor $(if ($testsFail -gt 0) { $ColorRed } else { $ColorGreen })
    Write-Host ""
    
    if ($testsFail -eq 0) {
        Write-Host "✓ All tests passed successfully!" -ForegroundColor $ColorGreen
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor $ColorBlue
        Write-Host "  1. Review output files in: $OUTPUT_DIR/" -ForegroundColor $ColorBlue
        Write-Host "  2. Run application with: docker-compose up" -ForegroundColor $ColorBlue
        Write-Host "  3. Access Spark UI at: http://localhost:4040" -ForegroundColor $ColorBlue
        Write-Host ""
        Write-Host "Docker image is ready for deployment!" -ForegroundColor $ColorGreen
        exit 0
    } else {
        Write-Host "✗ $testsFail test(s) failed" -ForegroundColor $ColorRed
        Write-Host ""
        Write-Host "Troubleshooting:" -ForegroundColor $ColorYellow
        Write-Host "  - Check Docker installation: docker --version" -ForegroundColor $ColorYellow
        Write-Host "  - Start Docker Desktop from Start Menu" -ForegroundColor $ColorYellow
        Write-Host "  - Check available disk space" -ForegroundColor $ColorYellow
        Write-Host "  - Review Docker documentation: https://docs.docker.com" -ForegroundColor $ColorYellow
        Write-Host ""
        exit 1
    }
}

# Run main
Main
