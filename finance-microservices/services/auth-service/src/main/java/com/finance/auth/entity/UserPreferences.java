package com.finance.auth.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "user_preferences", uniqueConstraints = {
        @UniqueConstraint(name = "uk_user_preferences_user", columnNames = "user_id")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserPreferences {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false, length = 20)
    @Builder.Default
    private String theme = "light";

    @Column(name = "primary_color", length = 20)
    @Builder.Default
    private String primaryColor = "#3B82F6";

    @Column(name = "sidebar_collapsed", nullable = false)
    @Builder.Default
    private boolean sidebarCollapsed = false;

    @Column(name = "default_report_period", length = 20)
    @Builder.Default
    private String defaultReportPeriod = "month";

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "report_categories", columnDefinition = "jsonb")
    @Builder.Default
    private List<Long> reportCategories = new ArrayList<>();

    @Column(name = "report_include_charts", nullable = false)
    @Builder.Default
    private boolean reportIncludeCharts = true;

    @Column(name = "report_include_tables", nullable = false)
    @Builder.Default
    private boolean reportIncludeTables = true;

    @Column(name = "report_email_frequency", length = 20)
    @Builder.Default
    private String reportEmailFrequency = "never";

    @Column(name = "notify_budget_exceeded", nullable = false)
    @Builder.Default
    private boolean notifyBudgetExceeded = true;

    @Column(name = "notify_large_transaction", nullable = false)
    @Builder.Default
    private boolean notifyLargeTransaction = true;

    @Column(name = "notify_anomaly_detected", nullable = false)
    @Builder.Default
    private boolean notifyAnomalyDetected = true;

    @Column(name = "large_transaction_threshold", precision = 15, scale = 2)
    @Builder.Default
    private BigDecimal largeTransactionThreshold = new BigDecimal("1000000");

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "dashboard_widgets", columnDefinition = "jsonb")
    @Builder.Default
    private List<String> dashboardWidgets = new ArrayList<>();

    @Column(name = "dashboard_chart_type", length = 20)
    @Builder.Default
    private String dashboardChartType = "line";

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
}
