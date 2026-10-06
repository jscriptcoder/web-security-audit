package com.example.orders.mail

import org.springframework.mail.SimpleMailMessage
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.stereotype.Component

@Component
class Mailer(private val sender: JavaMailSender) {
    fun send(to: String, subject: String, body: String) {
        sender.send(SimpleMailMessage().apply {
            setTo(to)
            setFrom("no-reply@shop.example.com")
            setSubject(subject)
            setText(body)
        })
    }
}
