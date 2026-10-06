package com.example.orders.data

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param

interface OrderRepository : JpaRepository<Order, Long> {
    fun findAllByCustomerId(customerId: String): List<Order>
    fun findByIdAndCustomerId(id: Long, customerId: String): Order?
}

interface UserRepository : JpaRepository<User, Long> {
    @Query("select u from User u where lower(u.email) = lower(:email)")
    fun findByEmail(@Param("email") email: String): User?
}
