$content = Get-Content "psql.html" -Raw

# Extract all TOC hrefs
$tocLinks = [regex]::Matches($content, 'href="#([^"]+)"') | ForEach-Object { $_.Groups[1].Value }

# Extract all content IDs  
$contentIds = [regex]::Matches($content, '\sid="([^"]+)"') | ForEach-Object { $_.Groups[1].Value }

# Filter to chapters 4, 5, 6, 7 - define all expected IDs
$ch4Ids = @(
    'sql-syntax', 'lexical-structure', 'identifiers-keywords', 'constants', 
    'operators', 'special-characters', 'comments', 'operator-precedence',
    'value-expressions', 'column-references', 'positional-parameters', 'subscripts',
    'field-selection', 'operator-invocations', 'function-calls', 'aggregate-expressions',
    'window-function-calls', 'type-casts', 'collation-expressions', 'scalar-subqueries',
    'array-constructors', 'row-constructors', 'expression-evaluation-rules',
    'calling-functions', 'positional-notation', 'named-notation', 'mixed-notation'
)

$ch5Ids = @(
    'data-definition', 'table-basics', 'default-values', 'identity-columns', 
    'generated-columns', 'constraints', 'check-constraints', 'not-null-constraints',
    'unique-constraints', 'primary-keys', 'foreign-keys', 'exclusion-constraints',
    'system-columns', 'modifying-tables', 'adding-column', 'removing-column',
    'adding-constraint', 'removing-constraint', 'changing-column-default',
    'changing-column-type', 'renaming-column', 'renaming-table', 'privileges',
    'row-security-policies', 'schemas', 'creating-schema', 'public-schema',
    'schema-search-path', 'schemas-privileges', 'system-catalog-schema',
    'usage-patterns', 'portability', 'inheritance', 'inheritance-caveats',
    'table-partitioning', 'partitioning-overview', 'declarative-partitioning',
    'partitioning-inheritance', 'partition-pruning', 'partition-constraint-exclusion',
    'declarative-best-practices', 'foreign-data', 'other-database-objects',
    'dependency-tracking'
)

$ch6Ids = @(
    'data-manipulation', 'inserting-data', 'updating-data', 
    'deleting-data', 'returning-data'
)

$ch7Ids = @(
    'queries', 'queries-overview', 'query-overview', 'table-expressions',
    'from-clause', 'where-clause', 'group-by-having', 'grouping-sets',
    'window-functions', 'select-lists', 'select-list-items', 'column-labels',
    'distinct', 'combining-queries', 'sorting-rows', 'limit-offset',
    'values-lists', 'with-queries', 'select-in-with', 'recursive-queries',
    'cte-materialization', 'data-modifying-with'
)

$allCh4567Ids = $ch4Ids + $ch5Ids + $ch6Ids + $ch7Ids

# Filter TOC links for these chapters
$ch4567TocLinks = $tocLinks | Where-Object { $_ -in $allCh4567Ids }

# Filter content IDs for these chapters
$ch4567ContentIds = $contentIds | Where-Object { $_ -in $allCh4567Ids }

Write-Output "=========================================="
Write-Output "  SIDEMENU LINK VERIFICATION REPORT"
Write-Output "  Chapters 4, 5, 6, and 7"
Write-Output "=========================================="
Write-Output ""

# Summary Statistics
Write-Output "SUMMARY STATISTICS:"
Write-Output "-------------------"
Write-Output "Total TOC links found (Ch 4-7): $($ch4567TocLinks.Count)"
Write-Output "Total content IDs found (Ch 4-7): $($ch4567ContentIds.Count)"
Write-Output ""

# Check for missing IDs
$missingIds = @()
foreach ($link in $ch4567TocLinks) {
    if ($link -notin $contentIds) {
        $missingIds += $link
    }
}

Write-Output "MISSING IDs (TOC links without matching content):"
Write-Output "--------------------------------------------------"
if ($missingIds.Count -eq 0) {
    Write-Output "✓ None - All TOC links have matching content IDs!"
} else {
    Write-Output "⚠ Found $($missingIds.Count) missing ID(s):"
    $missingIds | Sort-Object | ForEach-Object { Write-Output "  - $_" }
}
Write-Output ""

# Check for orphan IDs
$orphanIds = @()
foreach ($id in $ch4567ContentIds) {
    if ($id -notin $ch4567TocLinks) {
        $orphanIds += $id
    }
}

Write-Output "ORPHAN IDs (content IDs not referenced in TOC):"
Write-Output "------------------------------------------------"
if ($orphanIds.Count -eq 0) {
    Write-Output "✓ None - All content IDs are referenced in TOC!"
} else {
    Write-Output "⚠ Found $($orphanIds.Count) orphan ID(s):"
    $orphanIds | Sort-Object | ForEach-Object { Write-Output "  - $_" }
}
Write-Output ""

# Detailed breakdown by chapter
Write-Output "DETAILED BREAKDOWN BY CHAPTER:"
Write-Output "-------------------------------"

foreach ($chNum in 4..7) {
    $chIds = switch ($chNum) {
        4 { $ch4Ids }
        5 { $ch5Ids }
        6 { $ch6Ids }
        7 { $ch7Ids }
    }
    
    $chTocLinks = $tocLinks | Where-Object { $_ -in $chIds }
    $chContentIds = $contentIds | Where-Object { $_ -in $chIds }
    $chMissing = $chTocLinks | Where-Object { $_ -notin $contentIds }
    $chOrphan = $chContentIds | Where-Object { $_ -notin $chTocLinks }
    
    Write-Output ""
    Write-Output "Chapter $chNum"":"
    Write-Output "  TOC Links: $($chTocLinks.Count)"
    Write-Output "  Content IDs: $($chContentIds.Count)"
    Write-Output "  Missing: $($chMissing.Count)"
    Write-Output "  Orphans: $($chOrphan.Count)"
    
    if ($chMissing.Count -gt 0) {
        Write-Output "  Missing IDs: $($chMissing -join ', ')"
    }
    if ($chOrphan.Count -gt 0) {
        Write-Output "  Orphan IDs: $($chOrphan -join ', ')"
    }
}

Write-Output ""
Write-Output "=========================================="
Write-Output "FINAL VERIFICATION:"
Write-Output "=========================================="
if ($missingIds.Count -eq 0 -and $orphanIds.Count -eq 0) {
    Write-Output "✓ ALL LINKS ARE WORKING CORRECTLY!"
    Write-Output "✓ All TOC links have matching content IDs"
    Write-Output "✓ All content IDs are referenced in the TOC"
} else {
    Write-Output "⚠ ISSUES FOUND - See details above"
}
Write-Output "=========================================="
