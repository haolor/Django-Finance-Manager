package com.finance.auth.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;

@Getter
@Setter
@ConfigurationProperties(prefix = "finance.security.jwt")
public class JwtProperties {

    private String secret;
    private String issuer = "finance-auth-service";
    private Duration accessTokenTtl = Duration.ofHours(12);
}
