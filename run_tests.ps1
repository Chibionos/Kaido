# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first to set up the environment"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
.\.venv\Scripts\Activate.ps1

# Check if server script exists
$SERVER_SCRIPT = "nltest\server.py"
if (-not (Test-Path $SERVER_SCRIPT)) {
    Write-Host "Error: Server script not found at $SERVER_SCRIPT" -ForegroundColor Red
    exit 1
}

# Function to run tests in a directory
function Run-Tests {
    param (
        [string]$TestDir
    )
    
    $total = 0
    $passed = 0
    $failed = 0
    $failedTests = @()
    
    # Find all .test.md files
    $testFiles = Get-ChildItem -Path $TestDir -Filter "*.test.md" -Recurse
    
    foreach ($testFile in $testFiles) {
        $total++
        Write-Host "`nRunning test: $($testFile.FullName)" -ForegroundColor Blue
        Write-Host "----------------------------------------"
        
        try {
            nltest run $testFile.FullName $SERVER_SCRIPT
            if ($LASTEXITCODE -eq 0) {
                $passed++
                Write-Host "✓ Test passed" -ForegroundColor Green
            } else {
                $failed++
                $failedTests += $testFile.FullName
                Write-Host "✗ Test failed" -ForegroundColor Red
            }
        } catch {
            $failed++
            $failedTests += $testFile.FullName
            Write-Host "✗ Test failed with error: $_" -ForegroundColor Red
        }
    }
    
    # Print summary
    Write-Host "`nTest Summary" -ForegroundColor White
    Write-Host "----------------------------------------"
    Write-Host "Total tests:  $total"
    Write-Host "Passed:       $passed" -ForegroundColor Green
    
    if ($failed -gt 0) {
        Write-Host "Failed:       $failed" -ForegroundColor Red
        Write-Host "`nFailed tests:" -ForegroundColor Red
        foreach ($test in $failedTests) {
            Write-Host "  ✗ $test" -ForegroundColor Red
        }
    } else {
        Write-Host "Failed:       $failed" -ForegroundColor Green
        Write-Host "`nAll tests passed!" -ForegroundColor Green
    }
}

# Default test directory
$TEST_DIR = "tests"

# Check if test directory exists
if (-not (Test-Path $TEST_DIR)) {
    Write-Host "Error: Test directory not found at $TEST_DIR" -ForegroundColor Red
    exit 1
}

# Check if ANTHROPIC_API_KEY is set
if (-not (Test-Path .env) -and -not $env:ANTHROPIC_API_KEY) {
    Write-Host "Error: ANTHROPIC_API_KEY not found" -ForegroundColor Red
    Write-Host "Please set your API key in .env file"
    exit 1
}

# Run the tests
Write-Host "Starting test run..." -ForegroundColor Blue
Run-Tests $TEST_DIR 