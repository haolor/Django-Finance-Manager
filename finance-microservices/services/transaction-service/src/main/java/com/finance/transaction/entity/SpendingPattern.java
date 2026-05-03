package com.finance.transaction.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;

@Entity
@Table(name = "spending_patterns", uniqueConstraints = {
        @UniqueConstraint(name = "uk_pattern_user_category", columnNames = {"user_id", "category_id"})
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SpendingPattern {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "category_id", nullable = false)
    private Long categoryId;

    @Column(name = "average_amount", precision = 15, scale = 2)
    private BigDecimal averageAmount;

    @Column(nullable = false)
    @Builder.Default
    private Integer frequency = 0;

    @Column(name = "last_transaction_date")
    private LocalDate lastTransactionDate;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;
}
