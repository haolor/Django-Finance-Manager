package com.finance.ai.config;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

@Getter
@Setter
@ConfigurationProperties(prefix = "finance.ai")
public class AiProperties {

    private String provider = "gemini";
    private String model = "gemini-2.0-flash";
}
