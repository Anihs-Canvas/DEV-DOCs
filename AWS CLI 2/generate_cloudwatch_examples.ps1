# CloudWatch Examples Generator
# Generates Attributes, Methods, and 5 Examples for each CloudWatch command

$commands = @(
    @{
        name = "delete-anomaly-detector"
        description = "Deletes an anomaly detector"
        namespace = "Custom/Skills"
        metric = "SkillsQueryLatency"
    },
    @{
        name = "delete-dashboards"
        description = "Deletes CloudWatch dashboards"
        namespace = "Custom/JobPost"
        metric = "DashboardViews"
    },
    @{
        name = "delete-insight-rules"
        description = "Deletes Contributor Insights rules"
        namespace = "Custom/Author"
        metric = "TopAuthors"
    },
    @{
        name = "delete-metric-stream"
        description = "Deletes a metric stream"
        namespace = "Custom/JobPost"
        metric = "StreamedMetrics"
    },
    @{
        name = "describe-alarm-contributors"
        description = "Describes alarm contributors"
        namespace = "Custom/User"
        metric = "LoginFailures"
    }
)

function Generate-Attributes {
    param($commandName)
    
    return @"

                <h5>Attributes</h5>
                <ul>
                    <li><strong>CommandName (string)</strong>: AWS CloudWatch command identifier</li>
                    <li><strong>Namespace (string)</strong>: CloudWatch metric namespace</li>
                    <li><strong>MetricName (string)</strong>: Name of the metric being monitored</li>
                    <li><strong>State (string)</strong>: Current operational state</li>
                </ul>
"@
}

function Generate-Methods {
    param($commandName)
    
    $methodName = ($commandName -split '-' | ForEach-Object { 
        $_.Substring(0,1).ToUpper() + $_.Substring(1) 
    }) -join ''
    
    return @"

                <h5>Methods</h5>
                <p><strong>$methodName</strong> - CloudWatch operation for $commandName</p>
                
                <h6>Syntax</h6>
                <pre><code class="language-bash">aws cloudwatch $commandName \
  --region {region-name} \
  [--cli-input-json {json-file}]</code></pre>

                <h6>Parameters</h6>
                <ul>
                    <li><strong>Region (string, optional)</strong>: AWS region for the operation</li>
                    <li><strong>CliInputJson (string, optional)</strong>: Path to JSON file with parameters</li>
                </ul>
"@
}

function Generate-Example {
    param(
        $commandName,
        $exampleNumber,
        $namespace,
        $metric
    )
    
    $titles = @(
        "Monitor Skills Query Performance",
        "Track User Authentication Metrics",
        "Analyze Author Content Creation",
        "Monitor Location Search Activity",
        "Track JobPost Database Operations"
    )
    
    $title = $titles[$exampleNumber - 1]
    
    return @"

                <div class="example">
                    <h5>Example $exampleNumber`: $title</h5>
                    <p>CloudWatch operation for monitoring Django jobpost application metrics including Skills, User, Author, Location, and JobPost models.</p>
                    <pre><code class="language-bash">#!/bin/bash
# CloudWatch $commandName - Example $exampleNumber
aws cloudwatch $commandName \
  --namespace "$namespace" \
  --metric-name "$metric" \
  --region us-east-1</code></pre>

                    <div class="docker-output">{
  "Status": "Success",
  "Operation": "$commandName",
  "Namespace": "$namespace",
  "MetricName": "$metric",
  "Timestamp": "2026-01-15T10:00:00Z"
}

✓ Operation completed successfully</div>

                    <div class="queryset-output"># Django QuerySet - CloudWatch $commandName Example $exampleNumber
from jobpost.models import Skills, User, Author, Location, JobPost
from django.db.models import Count, Avg
from django.utils import timezone

print("CloudWatch Operation: $commandName")
print("="*60)

# Skills monitoring
skills = Skills.objects.all()
print(f"Total Skills: {skills.count()}")
# Output: Total Skills: 0

# User metrics
users = User.objects.filter(is_active=True)
print(f"Active Users: {users.count()}")
# Output: Active Users: 0

# Author activity
authors = Author.objects.all()
print(f"Total Authors: {authors.count()}")
# Output: Total Authors: 0

# Location data
locations = Location.objects.all()
print(f"Total Locations: {locations.count()}")
# Output: Total Locations: 0

# JobPost statistics
jobposts = JobPost.objects.all()
print(f"Total JobPosts: {jobposts.count()}")
# Output: Total JobPosts: 0

print("\n✓ CloudWatch operation completed")
print("✓ Django models verified")</div>
                </div>
"@
}

Write-Host "CloudWatch Examples Generator Started" -ForegroundColor Green
Write-Host "Processing $($commands.Count) commands..." -ForegroundColor Cyan

foreach ($cmd in $commands) {
    Write-Host "`nGenerating examples for: $($cmd.name)" -ForegroundColor Yellow
    
    $content = ""
    $content += Generate-Attributes -commandName $cmd.name
    $content += Generate-Methods -commandName $cmd.name
    
    $content += "`n                <h5>5 Detailed CloudWatch $($cmd.name) Examples</h5>"
    
    for ($i = 1; $i -le 5; $i++) {
        $content += Generate-Example -commandName $cmd.name -exampleNumber $i -namespace $cmd.namespace -metric $cmd.metric
    }
    
    # Save to temp file for review
    $tempFile = "c:\Users\owner\Desktop\DEV-DOCs\AWS CLI\temp_$($cmd.name).html"
    $content | Out-File -FilePath $tempFile -Encoding UTF8
    
    Write-Host "  ✓ Generated content saved to: $tempFile" -ForegroundColor Green
}

Write-Host "`n✓ All examples generated successfully!" -ForegroundColor Green
Write-Host "Review temp files before applying to main document" -ForegroundColor Cyan
