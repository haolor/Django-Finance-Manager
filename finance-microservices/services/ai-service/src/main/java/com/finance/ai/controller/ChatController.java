package com.finance.ai.controller;

import com.finance.ai.config.AiProperties;
import com.finance.ai.dto.ChatRequest;
import com.finance.ai.dto.ChatResponse;
import com.finance.ai.feign.TransactionClient;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/v1")
@RequiredArgsConstructor
public class ChatController {

    private final ObjectProvider<ChatClient> chatClientProvider;
    private final TransactionClient transactionClient;
    private final AiProperties aiProperties;

    @PostMapping("/chat")
    public ChatResponse chat(@Valid @RequestBody ChatRequest request) {
        String context;
        try {
            context = transactionClient.financeContext();
        } catch (Exception ex) {
            log.warn("Không lấy được finance-context, fallback rỗng: {}", ex.getMessage());
            context = "{}";
        }

        ChatClient client = chatClientProvider.getIfAvailable();
        if (client == null) {
            return new ChatResponse(
                    request.message(),
                    "AI provider chưa cấu hình. Đặt GEMINI_API_KEY hoặc Vertex AI credentials.",
                    "stub",
                    "none"
            );
        }

        String reply = client.prompt()
                .system("Bạn là trợ lý tài chính cá nhân. Ngữ cảnh JSON: " + context)
                .user(request.message())
                .call()
                .content();

        return new ChatResponse(request.message(), reply, "gemini", aiProperties.getModel());
    }
}
