# Comprehensive Conversion Testing Script
$baseUrl = "http://localhost:8000"
$testResults = @()

function Test-Conversion {
    param($category, $file, $targetFormat, $conversionId = $null)
    
    try {
        # Upload file if no conversionId
        if (-not $conversionId) {
            $uploadUrl = "$baseUrl/api/upload"
            $response = curl -X POST $uploadUrl -F "file=@$file" 2>&1 | Out-String
            if ($response -match '"id":(\d+)') {
                $conversionId = $matches[1]
            } else {
                return @{Category=$category; File=$file; Target=$targetFormat; Status="❌ Upload Failed"; Error=$response}
            }
        }
        
        # Convert
        $convertUrl = "$baseUrl/api/$category/convert/$conversionId"
        if ($targetFormat) {
            $convertUrl += "?target_format=$targetFormat"
        }
        
        $result = curl -X POST $convertUrl -H "Content-Type: application/json" -d '{}' 2>&1 | Out-String
        
        if ($result -match '"status":"completed"' -or $result -match '"download_url"') {
            return @{Category=$category; File=$file; Target=$targetFormat; Status="✅ Success"; ConversionId=$conversionId}
        } else {
            return @{Category=$category; File=$file; Target=$targetFormat; Status="❌ Failed"; Error=$result; ConversionId=$conversionId}
        }
    } catch {
        return @{Category=$category; File=$file; Target=$targetFormat; Status="❌ Exception"; Error=$_.Exception.Message}
    }
}

Write-Host "🧪 Starting Comprehensive Testing..." -ForegroundColor Cyan

# 1. DOCUMENT CONVERSIONS
Write-Host "`n📄 Testing Documents..." -ForegroundColor Yellow
$testResults += Test-Conversion "documents" "test_files\test.txt" "pdf"
$testResults += Test-Conversion "documents" "test_files\test.csv" "xlsx"
$testResults += Test-Conversion "documents" "test_files\test.txt" "docx"

# 2. CODE CONVERSIONS
Write-Host "`n💻 Testing Code..." -ForegroundColor Yellow
$testResults += Test-Conversion "code" "test_files\test.json" "xml"
$testResults += Test-Conversion "code" "test_files\test.json" "yaml"
$testResults += Test-Conversion "code" "test_files\test.xml" "json"
$testResults += Test-Conversion "code" "test_files\test.csv" "json"

# 3. SECURITY
Write-Host "`n🔒 Testing Security..." -ForegroundColor Yellow
$testResults += Test-Conversion "security" "test_files\test.txt" "base64"
$testResults += Test-Conversion "security" "test_files\test.txt" "md5"
$testResults += Test-Conversion "security" "test_files\test.txt" "sha256"

# Display Results
Write-Host "`n`n📊 TEST RESULTS:" -ForegroundColor Cyan
Write-Host "=" * 80
foreach ($result in $testResults) {
    Write-Host "$($result.Status) $($result.Category)/$($result.File) → $($result.Target)"
    if ($result.Error) {
        Write-Host "   Error: $($result.Error.Substring(0, [Math]::Min(100, $result.Error.Length)))" -ForegroundColor Red
    }
}

Write-Host "`n✅ Passed: $(($testResults | Where-Object {$_.Status -like '*Success*'}).Count)"
Write-Host "❌ Failed: $(($testResults | Where-Object {$_.Status -like '*Failed*' -or $_.Status -like '*Exception*'}).Count)"
