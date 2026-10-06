package com.example.orders.data

import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.Id

@Entity
class User(
    @Id @GeneratedValue
    var id: Long? = null,
    var subject: String = "",
    var email: String = "",
)
