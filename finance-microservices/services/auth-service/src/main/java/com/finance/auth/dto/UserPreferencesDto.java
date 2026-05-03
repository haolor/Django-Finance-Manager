package com.finance.auth.dto;

import java.math.BigDecimal;
import java.util.List;

public record UserPreferencesDto(
        String theme,
        String primaryColor,
        boolean sidebarCollapsed,
        String defaultReportPeriod,
        List<Long> reportCategories,
        boolean reportIncludeCharts,
        boolean reportIncludeTables,
        String reportEmailFrequency,
        boolean notifyBudgetExceeded,
        boolean notifyLargeTransaction,
        boolean notifyAnomalyDetected,
        BigDecimal largeTransactionThreshold,
        List<String> dashboardWidgets,
        String dashboardChartType
) {
}
