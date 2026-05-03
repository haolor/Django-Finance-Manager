package com.finance.transaction.mapper;

import com.finance.transaction.dto.CategoryDto;
import com.finance.transaction.dto.TransactionDto;
import com.finance.transaction.entity.Category;
import com.finance.transaction.entity.Transaction;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface TransactionMapper {

    CategoryDto toDto(Category entity);

    Category toEntity(CategoryDto dto);

    TransactionDto toDto(Transaction entity);
}
