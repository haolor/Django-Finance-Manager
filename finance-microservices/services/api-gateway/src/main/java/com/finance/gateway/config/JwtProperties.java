package com.finance.gateway.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;

@Getter
@Setter
@ConfigurationProperties(prefix = "finance.security.jwt")
public class JwtProperties {

    /** HMAC secret (Base64 hoặc plain string, tối thiểu 32 ký tự cho HS256). */
    private String secret;

    /** Các path bắt đầu bằng giá trị này sẽ KHÔNG yêu cầu JWT. */
    private List<String> publicPaths = List.of(
            "/api/auth/register",
            "/api/auth/login",
            "/actuator/health",
            "/actuator/info"
    );
}
