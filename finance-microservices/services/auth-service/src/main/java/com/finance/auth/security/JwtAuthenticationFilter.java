package com.finance.auth.security;

import com.finance.auth.service.JwtService;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String BEARER_PREFIX = "Bearer ";
    private final JwtService jwtService;

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request,
                                    @NonNull HttpServletResponse response,
                                    @NonNull FilterChain filterChain) throws ServletException, IOException {
        String userIdHeader = request.getHeader("X-User-Id");
        String usernameHeader = request.getHeader("X-Username");

        if (userIdHeader != null && !userIdHeader.isBlank()) {
            authenticate(Long.parseLong(userIdHeader), usernameHeader);
        } else {
            String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
            if (authHeader != null && authHeader.startsWith(BEARER_PREFIX)) {
                String token = authHeader.substring(BEARER_PREFIX.length()).trim();
                try {
                    Claims claims = jwtService.parse(token);
                    Long userId = Long.parseLong(claims.getSubject());
                    Object usernameClaim = claims.get("username");
                    String username = usernameClaim == null ? "" : usernameClaim.toString();
                    authenticate(userId, username);
                } catch (JwtException | NumberFormatException ex) {
                    log.debug("JWT parse failed: {}", ex.getMessage());
                }
            }
        }
        filterChain.doFilter(request, response);
    }

    private void authenticate(Long userId, String username) {
        AuthenticatedUser principal = new AuthenticatedUser(userId, username == null ? "" : username);
        UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(principal, null, List.of());
        SecurityContextHolder.getContext().setAuthentication(auth);
    }
}
