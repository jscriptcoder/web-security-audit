package com.example.shop.config

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

private const val REQUESTS_PER_MINUTE = 30

@Component
class GraphQlRateLimitFilter : OncePerRequestFilter() {
    private val windows = ConcurrentHashMap<String, Pair<Long, AtomicInteger>>()

    override fun shouldNotFilter(request: HttpServletRequest): Boolean =
        request.requestURI != "/graphql"

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain,
    ) {
        val minute = System.currentTimeMillis() / 60_000
        val window = windows.compute(request.remoteAddr) { _, current ->
            if (current == null || current.first != minute) minute to AtomicInteger() else current
        }!!
        if (window.second.incrementAndGet() > REQUESTS_PER_MINUTE) {
            response.status = 429
            return
        }
        filterChain.doFilter(request, response)
    }
}
