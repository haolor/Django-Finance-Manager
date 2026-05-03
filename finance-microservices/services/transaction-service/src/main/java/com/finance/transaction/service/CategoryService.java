package com.finance.transaction.service;

import com.finance.transaction.dto.CategoryDto;
import com.finance.transaction.entity.Category;
import com.finance.transaction.exception.ApiException;
import com.finance.transaction.mapper.TransactionMapper;
import com.finance.transaction.repository.CategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CategoryService {

    private final CategoryRepository categoryRepository;
    private final TransactionMapper mapper;

    @Transactional(readOnly = true)
    public List<CategoryDto> findAll() {
        return categoryRepository.findAll().stream().map(mapper::toDto).toList();
    }

    @Transactional(readOnly = true)
    public CategoryDto findById(Long id) {
        return categoryRepository.findById(id)
                .map(mapper::toDto)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy danh mục"));
    }

    @Transactional
    public CategoryDto create(CategoryDto dto) {
        if (categoryRepository.findByName(dto.name()).isPresent()) {
            throw new ApiException(HttpStatus.CONFLICT, "Tên danh mục đã tồn tại");
        }
        Category saved = categoryRepository.save(mapper.toEntity(dto));
        return mapper.toDto(saved);
    }

    @Transactional
    public CategoryDto update(Long id, CategoryDto dto) {
        Category entity = categoryRepository.findById(id)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy danh mục"));
        entity.setName(dto.name());
        entity.setDescription(dto.description());
        entity.setIcon(dto.icon());
        entity.setColor(dto.color());
        entity.setType(dto.type());
        return mapper.toDto(categoryRepository.save(entity));
    }

    @Transactional
    public void delete(Long id) {
        if (!categoryRepository.existsById(id)) {
            throw new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy danh mục");
        }
        categoryRepository.deleteById(id);
    }
}
