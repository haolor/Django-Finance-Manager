package com.finance.ai.dto;

public record ChatResponse(
        String message,
        String response,
        String provider,
        String model
) {
}
