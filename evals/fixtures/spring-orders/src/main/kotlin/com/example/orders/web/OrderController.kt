package com.example.orders.web

import com.example.orders.data.Order
import com.example.orders.data.OrderRepository
import com.example.orders.data.OrderStatus
import org.springframework.http.HttpStatus
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.oauth2.jwt.Jwt
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.server.ResponseStatusException

@RestController
@RequestMapping("/api/orders")
class OrderController(private val orders: OrderRepository) {

    @GetMapping
    fun list(@AuthenticationPrincipal jwt: Jwt): List<Order> =
        orders.findAllByCustomerId(jwt.subject)

    @GetMapping("/{id}")
    fun get(@PathVariable id: Long): Order =
        orders.findById(id).orElseThrow { ResponseStatusException(HttpStatus.NOT_FOUND) }

    @PostMapping("/{id}/cancel")
    @Transactional
    fun cancel(@PathVariable id: Long, @AuthenticationPrincipal jwt: Jwt): Order {
        val order = orders.findByIdAndCustomerId(id, jwt.subject)
            ?: throw ResponseStatusException(HttpStatus.NOT_FOUND)
        if (order.status != OrderStatus.PLACED) {
            throw ResponseStatusException(HttpStatus.CONFLICT)
        }
        order.status = OrderStatus.CANCELLED
        return order
    }
}
