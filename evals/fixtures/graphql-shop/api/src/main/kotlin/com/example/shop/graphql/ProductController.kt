package com.example.shop.graphql

import com.example.shop.data.Customer
import com.example.shop.data.CustomerRepository
import com.example.shop.data.Product
import com.example.shop.data.ProductRepository
import com.example.shop.data.Review
import com.example.shop.data.ReviewRepository
import org.springframework.data.domain.PageRequest
import org.springframework.graphql.data.method.annotation.Argument
import org.springframework.graphql.data.method.annotation.BatchMapping
import org.springframework.graphql.data.method.annotation.QueryMapping
import org.springframework.graphql.data.method.annotation.SchemaMapping
import org.springframework.stereotype.Controller

@Controller
class ProductController(
    private val products: ProductRepository,
    private val reviews: ReviewRepository,
    private val customers: CustomerRepository,
) {

    @QueryMapping
    fun product(@Argument id: Long): Product? = products.findById(id).orElse(null)

    @QueryMapping
    fun products(@Argument first: Int): List<Product> =
        products.findAll(PageRequest.of(0, first.coerceIn(1, 50))).content

    @SchemaMapping
    fun reviews(product: Product): List<Review> = reviews.findAllByProductId(product.id!!)

    @BatchMapping
    fun author(reviews: List<Review>): Map<Review, Customer> {
        val byId = customers.findAllById(reviews.map { it.authorId }).associateBy { it.id }
        return reviews.associateWith { byId.getValue(it.authorId) }
    }
}
