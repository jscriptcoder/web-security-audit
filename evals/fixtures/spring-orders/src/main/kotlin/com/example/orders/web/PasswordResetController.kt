package com.example.orders.web

import com.example.orders.data.UserRepository
import com.example.orders.mail.Mailer
import com.example.orders.security.ResetTokenService
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.servlet.support.ServletUriComponentsBuilder

data class ResetRequest(val email: String)

@RestController
class PasswordResetController(
    private val users: UserRepository,
    private val tokens: ResetTokenService,
    private val mailer: Mailer,
) {

    @PostMapping("/api/password-reset")
    @ResponseStatus(HttpStatus.ACCEPTED)
    fun requestReset(@RequestBody body: ResetRequest) {
        val user = users.findByEmail(body.email) ?: return
        val token = tokens.issue(user)
        val link = ServletUriComponentsBuilder.fromCurrentContextPath()
            .path("/reset")
            .queryParam("token", token)
            .toUriString()
        mailer.send(user.email, "Reset your password", "Use this link within 30 minutes: $link")
    }
}
