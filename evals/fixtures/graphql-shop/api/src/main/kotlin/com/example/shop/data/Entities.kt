package com.example.shop.data

import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.Id
import java.math.BigDecimal

@Entity
class Customer(
    @Id @GeneratedValue var id: Long? = null,
    var subject: String = "",
    var displayName: String = "",
    var email: String = "",
    var phone: String? = null,
    var creditBalance: BigDecimal = BigDecimal.ZERO,
)

@Entity
class Product(
    @Id @GeneratedValue var id: Long? = null,
    var name: String = "",
    var price: BigDecimal = BigDecimal.ZERO,
)

@Entity
class Review(
    @Id @GeneratedValue var id: Long? = null,
    var productId: Long = 0,
    var authorId: Long = 0,
    var rating: Int = 0,
    var body: String = "",
)

@Entity
class Order(
    @Id @GeneratedValue var id: Long? = null,
    var customerId: Long = 0,
    var total: BigDecimal = BigDecimal.ZERO,
    var status: String = "PLACED",
    var shippingAddress: String = "",
    var internalNotes: String? = null,
)

@Entity
class GiftCard(
    @Id @GeneratedValue var id: Long? = null,
    var code: String = "",
    var amount: BigDecimal = BigDecimal.ZERO,
    var redeemed: Boolean = false,
)
