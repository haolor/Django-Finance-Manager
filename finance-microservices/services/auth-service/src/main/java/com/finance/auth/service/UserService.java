package com.finance.auth.service;

import com.finance.auth.dto.UserDto;
import com.finance.auth.dto.UserPreferencesDto;
import com.finance.auth.entity.User;
import com.finance.auth.entity.UserPreferences;
import com.finance.auth.exception.ApiException;
import com.finance.auth.mapper.UserMapper;
import com.finance.auth.repository.UserPreferencesRepository;
import com.finance.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final UserPreferencesRepository preferencesRepository;
    private final UserMapper userMapper;

    @Transactional(readOnly = true)
    public UserDto profile(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Không tìm thấy người dùng"));
        return userMapper.toDto(user);
    }

    @Transactional(readOnly = true)
    public UserPreferencesDto preferences(Long userId) {
        UserPreferences pref = preferencesRepository.findByUserId(userId)
                .orElseGet(() -> UserPreferences.builder().userId(userId).build());
        return userMapper.toDto(pref);
    }

    @Transactional
    public UserPreferencesDto updatePreferences(Long userId, UserPreferencesDto patch) {
        UserPreferences pref = preferencesRepository.findByUserId(userId)
                .orElseGet(() -> UserPreferences.builder().userId(userId).build());

        Optional.ofNullable(patch.theme()).ifPresent(pref::setTheme);
        Optional.ofNullable(patch.primaryColor()).ifPresent(pref::setPrimaryColor);
        pref.setSidebarCollapsed(patch.sidebarCollapsed());
        Optional.ofNullable(patch.defaultReportPeriod()).ifPresent(pref::setDefaultReportPeriod);
        pref.setReportCategories(patch.reportCategories() != null ? patch.reportCategories() : new ArrayList<>());
        pref.setReportIncludeCharts(patch.reportIncludeCharts());
        pref.setReportIncludeTables(patch.reportIncludeTables());
        Optional.ofNullable(patch.reportEmailFrequency()).ifPresent(pref::setReportEmailFrequency);
        pref.setNotifyBudgetExceeded(patch.notifyBudgetExceeded());
        pref.setNotifyLargeTransaction(patch.notifyLargeTransaction());
        pref.setNotifyAnomalyDetected(patch.notifyAnomalyDetected());
        Optional.ofNullable(patch.largeTransactionThreshold()).ifPresent(pref::setLargeTransactionThreshold);
        pref.setDashboardWidgets(patch.dashboardWidgets() != null ? patch.dashboardWidgets() : new ArrayList<>());
        Optional.ofNullable(patch.dashboardChartType()).ifPresent(pref::setDashboardChartType);

        UserPreferences saved = preferencesRepository.save(pref);
        return userMapper.toDto(saved);
    }
}
