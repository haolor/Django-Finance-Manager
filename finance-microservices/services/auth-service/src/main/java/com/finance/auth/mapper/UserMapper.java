package com.finance.auth.mapper;

import com.finance.auth.dto.UserDto;
import com.finance.auth.dto.UserPreferencesDto;
import com.finance.auth.entity.User;
import com.finance.auth.entity.UserPreferences;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface UserMapper {

    UserDto toDto(User user);

    UserPreferencesDto toDto(UserPreferences preferences);
}
