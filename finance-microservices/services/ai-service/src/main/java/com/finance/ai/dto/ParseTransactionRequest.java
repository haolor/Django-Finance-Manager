package com.finance.ai.dto;

import jakarta.validation.constraints.NotBlank;

public record ParseTransactionRequest(@NotBlank String text) {
}
