package com.finance.transaction.dto;

import com.finance.transaction.entity.CategoryType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CategoryDto(
        Long id,
        @NotBlank @Size(max = 100) String name,
        String description,
        @Size(max = 50) String icon,
        @Size(max = 20) String color,
        @NotNull CategoryType type
) {
}
