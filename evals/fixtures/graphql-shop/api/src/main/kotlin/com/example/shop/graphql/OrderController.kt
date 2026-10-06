package com.example.shop.graphql

import com.example.shop.data.Customer
import com.example.shop.data.CustomerRepository
import com.example.shop.data.Order
import com.example.shop.data.OrderRepository
import org.springframework.graphql.data.method.annotation.Argument
import org.springframework.graphql.data.method.annotation.QueryMapping
import org.springframework.graphql.data.method.annotation.SchemaMapping
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.oauth2.jwt.Jwt
import org.springframework.stereotype.Controller

@Controller
class OrderController(
    private val orders: OrderRepository,
    private val customers: CustomerRepository,
) {

    @QueryMapping
    @PreAuthorize("isAuthenticated()")
    fun order(@Argument id: Long, @AuthenticationPrincipal jwt: Jwt): Order? {
        val me = customers.findBySubject(jwt.subject) ?: return null
        return orders.findByIdAndCustomerId(id, me.id!!)
    }

    @SchemaMapping(typeName = "Order")
    fun customer(order: Order): Customer = customers.findById(order.customerId).orElseThrow()

    @SchemaMapping(typeName = "Order")
    @PreAuthorize("hasAuthority('SCOPE_support')")
    fun internalNotes(order: Order): String? = order.internalNotes
}
