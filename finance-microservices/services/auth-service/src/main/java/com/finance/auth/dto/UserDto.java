package com.finance.auth.dto;

import java.time.Instant;

public record UserDto(
        Long id,
        String username,
        String email,
        String firstName,
        String lastName,
        boolean active,
        Instant createdAt
) {
}
