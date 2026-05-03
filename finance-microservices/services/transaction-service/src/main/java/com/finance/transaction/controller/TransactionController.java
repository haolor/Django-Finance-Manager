package com.finance.transaction.controller;

import com.finance.transaction.dto.PageResponse;
import com.finance.transaction.dto.TransactionDto;
import com.finance.transaction.security.AuthenticatedUser;
import com.finance.transaction.service.TransactionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Pageable;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;

    @GetMapping
    public PageResponse<TransactionDto> list(
            AuthenticatedUser user,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate fromDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate toDate,
            Pageable pageable
    ) {
        return transactionService.search(user.id(), categoryId, fromDate, toDate, pageable);
    }

    @GetMapping("/{id}")
    public TransactionDto get(AuthenticatedUser user, @PathVariable Long id) {
        return transactionService.findById(user.id(), id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TransactionDto create(AuthenticatedUser user, @Valid @RequestBody TransactionDto dto) {
        return transactionService.create(user.id(), dto);
    }

    @PutMapping("/{id}")
    public TransactionDto update(AuthenticatedUser user,
                                 @PathVariable Long id,
                                 @Valid @RequestBody TransactionDto dto) {
        return transactionService.update(user.id(), id, dto);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(AuthenticatedUser user, @PathVariable Long id) {
        transactionService.delete(user.id(), id);
    }
}
