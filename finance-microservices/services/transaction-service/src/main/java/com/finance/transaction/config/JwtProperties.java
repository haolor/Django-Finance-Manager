package com.finance.transaction.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

@Getter
@Setter
@ConfigurationProperties(prefix = "finance.security.jwt")
public class JwtProperties {

    private String secret;
}
