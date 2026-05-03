package com.finance.auth.controller;

import com.finance.auth.dto.AuthResponse;
import com.finance.auth.dto.LoginRequest;
import com.finance.auth.dto.RegisterRequest;
import com.finance.auth.dto.UserDto;
import com.finance.auth.dto.UserPreferencesDto;
import com.finance.auth.security.AuthenticatedUser;
import com.finance.auth.service.AuthService;
import com.finance.auth.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final UserService userService;

    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public AuthResponse register(@Valid @RequestBody RegisterRequest request) {
        return authService.register(request);
    }

    @PostMapping("/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request);
    }

    @GetMapping("/profile")
    public UserDto profile(AuthenticatedUser user) {
        return userService.profile(user.id());
    }

    @GetMapping("/preferences")
    public UserPreferencesDto getPreferences(AuthenticatedUser user) {
        return userService.preferences(user.id());
    }

    @PutMapping("/preferences")
    public ResponseEntity<UserPreferencesDto> updatePreferences(
            AuthenticatedUser user,
            @Valid @RequestBody UserPreferencesDto patch
    ) {
        return ResponseEntity.ok(userService.updatePreferences(user.id(), patch));
    }
}
