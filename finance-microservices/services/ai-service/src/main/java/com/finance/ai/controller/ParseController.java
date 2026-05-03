package com.finance.ai.controller;

import com.finance.ai.dto.ParseTransactionRequest;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * TODO: dùng Spring AI structured output để extract amount/category/date từ text,
 * sau đó gọi {@code TransactionClient.create(...)} để lưu giao dịch.
 */
@RestController
@RequestMapping("/v1")
public class ParseController {

    @PostMapping("/parse-transaction")
    public ResponseEntity<Map<String, Object>> parse(@Valid @RequestBody ParseTransactionRequest request) {
        return ResponseEntity.status(501).body(Map.of(
                "detail", "ParseTransaction chưa được triển khai",
                "input", request.text()
        ));
    }
}
