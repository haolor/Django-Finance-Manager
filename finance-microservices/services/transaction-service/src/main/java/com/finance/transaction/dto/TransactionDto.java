package com.finance.transaction.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PastOrPresent;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;

public record TransactionDto(
        Long id,
        Long userId,
        Long categoryId,
        @NotNull @DecimalMin(value = "0.01", inclusive = true) BigDecimal amount,
        String description,
        @NotNull @PastOrPresent LocalDate transactionDate,
        String originalNlpInput,
        Instant createdAt,
        Instant updatedAt
) {
}
