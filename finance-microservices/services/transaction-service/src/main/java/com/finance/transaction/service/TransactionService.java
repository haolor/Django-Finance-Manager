package com.finance.transaction.service;

import com.finance.transaction.dto.PageResponse;
import com.finance.transaction.dto.TransactionDto;
import com.finance.transaction.entity.Transaction;
import com.finance.transaction.exception.ApiException;
import com.finance.transaction.mapper.TransactionMapper;
import com.finance.transaction.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class TransactionService {

    private final TransactionRepository repository;
    private final TransactionMapper mapper;

    @Transactional(readOnly = true)
    public PageResponse<TransactionDto> search(Long userId,
                                               Long categoryId,
                                               LocalDate fromDate,
                                               LocalDate toDate,
                                               Pageable pageable) {
        Page<TransactionDto> page = repository
                .search(userId, categoryId, fromDate, toDate, pageable)
                .map(mapper::toDto);
        return PageResponse.from(page);
    }

    @Transactional(readOnly = true)
    public TransactionDto findById(Long userId, Long id) {
        return repository.findByIdAndUserId(id, userId)
                .map(mapper::toDto)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy giao dịch"));
    }

    @Transactional
    public TransactionDto create(Long userId, TransactionDto dto) {
        Transaction tx = Transaction.builder()
                .userId(userId)
                .categoryId(dto.categoryId())
                .amount(dto.amount())
                .description(dto.description())
                .transactionDate(dto.transactionDate())
                .originalNlpInput(dto.originalNlpInput())
                .build();
        return mapper.toDto(repository.save(tx));
    }

    @Transactional
    public TransactionDto update(Long userId, Long id, TransactionDto dto) {
        Transaction tx = repository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy giao dịch"));
        tx.setCategoryId(dto.categoryId());
        tx.setAmount(dto.amount());
        tx.setDescription(dto.description());
        tx.setTransactionDate(dto.transactionDate());
        tx.setOriginalNlpInput(dto.originalNlpInput());
        return mapper.toDto(repository.save(tx));
    }

    @Transactional
    public void delete(Long userId, Long id) {
        Transaction tx = repository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy giao dịch"));
        repository.delete(tx);
    }
}
