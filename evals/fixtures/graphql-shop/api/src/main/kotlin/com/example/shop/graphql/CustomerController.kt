package com.example.shop.graphql

import com.example.shop.data.Customer
import com.example.shop.data.CustomerRepository
import com.example.shop.data.Order
import com.example.shop.data.OrderRepository
import org.springframework.graphql.data.method.annotation.QueryMapping
import org.springframework.graphql.data.method.annotation.SchemaMapping
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.oauth2.jwt.Jwt
import org.springframework.stereotype.Controller

@Controller
class CustomerController(
    private val customers: CustomerRepository,
    private val orders: OrderRepository,
) {

    @QueryMapping
    @PreAuthorize("isAuthenticated()")
    fun me(@AuthenticationPrincipal jwt: Jwt): Customer? = customers.findBySubject(jwt.subject)

    @SchemaMapping(typeName = "Customer")
    fun orders(customer: Customer): List<Order> = orders.findAllByCustomerId(customer.id!!)
}
