<#
.Synopsis
    Build script

.Description
    TASKS AND REQUIREMENTS
    Initialize and Clean repository
    Create and Acrivate Virtual Environment
    Restore packages, workflows, tools
    Format code
    Build projects and the solution
    Run Tests
    Pack
    Publish
#>

[System.Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSReviewUnusedParameter', '', Justification = 'Parameter is used actually.')]
param(
    # Build Version
    [Parameter()]
    [string]
    $Version,
    # Build Instance
    [Parameter()]
    [string]
    $Instance
)

Set-StrictMode -Version Latest

# Synopsis: Publish Docker images
Task Publish Pack, {
    $state = Import-Clixml -Path ".\.trash\$Instance\state.clixml"
    $dockerImageVersionTag = $state.DockerImageVersionTag
    $dockerImageLatestTag = $state.DockerImageLatestTag
    $dockerImageVersionArchiveName = $state.DockerImageVersionArchiveName
    $dockerImageLatestArchiveName = $state.DockerImageLatestArchiveName
    $dockerImageVersionArchive = Resolve-Path -Path ".\.trash\$Instance\artifacts\$dockerImageVersionArchiveName"
    $dockerImageLatestArchive = Resolve-Path -Path ".\.trash\$Instance\artifacts\$dockerImageLatestArchiveName"

    Exec { docker image load --input $dockerImageVersionArchive }
    Exec { docker image load --input $dockerImageLatestArchive }

    if ($null -eq $env:DOCKER_ACCESS_TOKEN) {
        Import-Module -Name Microsoft.PowerShell.SecretManagement
        $credential = Get-Secret -Name 'Ergo-DockerHub-Credential'
    }
    else {
        $securePassword = New-Object SecureString
        foreach ($char in $env:DOCKER_ACCESS_TOKEN.ToCharArray()) {
            $securePassword.AppendChar($char)
        }
        $credential = [PSCredential]::New('tiksn', $securePassword)
    }

    $username = $credential.UserName
    $password = $credential.GetNetworkCredential().Password

    Exec { docker login --username $username --password $password }
    Exec { docker push $dockerImageVersionTag }
    Exec { docker push $dockerImageLatestTag }
}

# Synopsis: Pack NuGet package
Task Pack Build, Test, {
    $state = Import-Clixml -Path ".\.trash\$Instance\state.clixml"
    $dockerImageName = $state.DockerImageName
    $nextVersion = $state.NextVersion
    $dockerFilePath = Resolve-Path -Path '.\Dockerfile'

    $dockerImageVersionTag = "$($dockerImageName):$nextVersion"
    $dockerImageLatestTag = "$($dockerImageName):latest"

    $dockerImageVersionArchiveName = $state.DockerImageVersionArchiveName
    $dockerImageLatestArchiveName = $state.DockerImageLatestArchiveName
    $dockerImageVersionArchive = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(".\.trash\$Instance\artifacts\$dockerImageVersionArchiveName")
    $dockerImageLatestArchive = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(".\.trash\$Instance\artifacts\$dockerImageLatestArchiveName")

    Exec { docker buildx build --file $dockerFilePath --tag $dockerImageVersionTag --tag $dockerImageLatestTag . }
    Exec { docker image save --output $dockerImageVersionArchive $dockerImageVersionTag }
    Exec { docker image save --output $dockerImageLatestArchive $dockerImageLatestTag }

    $state.DockerImageVersionTag = $dockerImageVersionTag
    $state.DockerImageLatestTag = $dockerImageLatestTag

    $state | Export-Clixml -Path ".\.trash\$Instance\state.clixml"
    Write-Output $state
}

# Synopsis: Test
Task Test UnitTest, FunctionalTest, IntegrationTest

# Synopsis: Integration Test
Task IntegrationTest Build, {
    if (-not $env:CI) {
    }
}

# Synopsis: Functional Test
Task FunctionalTest Build, {
}

# Synopsis: Unit Test
Task UnitTest Build, {
}

# Synopsis: Build
Task Build Format, BuildApp, {
}

# Synopsis: Build App
Task BuildApp EstimateVersion, {
}

# Synopsis: Estimate Next Version
Task EstimateVersion Restore, {
    $state = Import-Clixml -Path ".\.trash\$Instance\state.clixml"
    if ($Version) {
        $state.NextVersion = [System.Management.Automation.SemanticVersion]$Version
    }
    else {
        $gitversion = Exec { git describe --tags --dirty --always }
        $state.NextVersion = [System.Management.Automation.SemanticVersion]::Parse($gitversion)
    }

    $state | Export-Clixml -Path ".\.trash\$Instance\state.clixml"
    Write-Output "Next version estimated to be $($state.NextVersion)"
    Write-Output $state
}

# Synopsis: Format
Task Format Restore, FormatWhitespace

# Synopsis: Format Whitespace
Task FormatWhitespace Restore, {
}

# Synopsis: Restore
Task Restore RestorePackages

# Synopsis: Restore packages
Task RestorePackages Clean, {
    if ($IsWindows) {
        .\.env\Scripts\activate.ps1
    }
    elseif ($IsLinux) {
        Exec { ls .env -R -a }
        Exec { .\.env\bin\activate.ps1 }
    }

    Exec { python -m pip install --upgrade pip }
    Exec { pip install -r requirements.txt }
}

# Synopsis: Clean previous build leftovers
Task Clean ActivateVirtualEnv, {
    Get-ChildItem -Directory
    | Where-Object { -not $_.Name.StartsWith('.') }
    | ForEach-Object { Get-ChildItem -Path $_ -Recurse -Directory }
    | Where-Object { ( $_.Name -eq '__pycache__') }
    | ForEach-Object { Remove-Item -Path $_ -Recurse -Force }
}

# Synopsis: Activate Virtual Environment
Task ActivateVirtualEnv CreateVirtualEnv, {
    if ($IsWindows) {
        .\.env\Scripts\activate.ps1
    }
    elseif ($IsLinux) {
        Exec { ls .env -R -a }
        Exec { .\.env\bin\activate.ps1 }
    }
}

# Synopsis: Create Virtual Environment
Task CreateVirtualEnv Init, {
    Exec { pip install virtualenv }
    Exec { virtualenv .env }
}

# Synopsis: Initialize folders and variables
Task Init {
    $trashFolder = Join-Path -Path . -ChildPath '.trash'
    $trashFolder = Join-Path -Path $trashFolder -ChildPath $Instance
    New-Item -Path $trashFolder -ItemType Directory | Out-Null
    $trashFolder = Resolve-Path -Path $trashFolder

    $buildArtifactsFolder = Join-Path -Path $trashFolder -ChildPath 'artifacts'
    New-Item -Path $buildArtifactsFolder -ItemType Directory | Out-Null

    $state = [PSCustomObject]@{
        NextVersion                   = $null
        TrashFolder                   = $trashFolder
        BuildArtifactsFolder          = $buildArtifactsFolder
        DockerImageName               = 'tiksn/ergo'
        DockerImageVersionTag         = $null
        DockerImageLatestTag          = $null
        DockerImageVersionArchiveName = 'tiksn-ergo-version.tar'
        DockerImageLatestArchiveName  = 'tiksn-ergo-latest.tar'
    }

    $state | Export-Clixml -Path ".\.trash\$Instance\state.clixml"
    Write-Output $state
}
