package com.example.orders.security

import com.example.orders.data.User
import org.springframework.stereotype.Service
import java.security.MessageDigest
import java.security.SecureRandom
import java.time.Duration
import java.time.Instant
import java.util.Base64
import java.util.concurrent.ConcurrentHashMap

@Service
class ResetTokenService {
    private val random = SecureRandom()
    private val pending = ConcurrentHashMap<String, Pair<Long, Instant>>()

    fun issue(user: User): String {
        val bytes = ByteArray(32).also(random::nextBytes)
        val token = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes)
        pending.entries.removeIf { it.value.first == user.id }
        pending[hash(token)] = user.id!! to Instant.now().plus(Duration.ofMinutes(30))
        return token
    }

    fun consume(token: String): Long? {
        val entry = pending.remove(hash(token)) ?: return null
        return entry.first.takeIf { Instant.now().isBefore(entry.second) }
    }

    private fun hash(token: String): String =
        Base64.getEncoder().encodeToString(MessageDigest.getInstance("SHA-256").digest(token.toByteArray()))
}
