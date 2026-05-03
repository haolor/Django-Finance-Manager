package com.finance.ai.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

@FeignClient(name = "transaction-service")
public interface TransactionClient {

    /**
     * TODO: cài endpoint thật {@code GET /api/ai/finance-context} trong transaction-service.
     * Trả JSON tổng hợp tài chính dùng cho prompt LLM.
     */
    @GetMapping("/api/ai/finance-context")
    String financeContext();
}
