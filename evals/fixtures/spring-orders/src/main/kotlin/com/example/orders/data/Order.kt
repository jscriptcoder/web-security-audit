package com.example.orders.data

import jakarta.persistence.Entity
import jakarta.persistence.EnumType
import jakarta.persistence.Enumerated
import jakarta.persistence.GeneratedValue
import jakarta.persistence.Id
import java.math.BigDecimal
import java.time.Instant

enum class OrderStatus { PLACED, SHIPPED, CANCELLED }

@Entity
class Order(
    @Id @GeneratedValue
    var id: Long? = null,
    var customerId: String = "",
    var shippingAddress: String = "",
    var total: BigDecimal = BigDecimal.ZERO,
    @Enumerated(EnumType.STRING)
    var status: OrderStatus = OrderStatus.PLACED,
    var createdAt: Instant = Instant.now(),
)
