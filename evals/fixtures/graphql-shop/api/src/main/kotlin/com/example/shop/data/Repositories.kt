package com.example.shop.data

import org.springframework.data.jpa.repository.JpaRepository

interface CustomerRepository : JpaRepository<Customer, Long> {
    fun findBySubject(subject: String): Customer?
}

interface ProductRepository : JpaRepository<Product, Long>

interface ReviewRepository : JpaRepository<Review, Long> {
    fun findAllByProductId(productId: Long): List<Review>
}

interface OrderRepository : JpaRepository<Order, Long> {
    fun findAllByCustomerId(customerId: Long): List<Order>
    fun findByIdAndCustomerId(id: Long, customerId: Long): Order?
}

interface GiftCardRepository : JpaRepository<GiftCard, Long> {
    fun findByCodeAndRedeemedFalse(code: String): GiftCard?
}
