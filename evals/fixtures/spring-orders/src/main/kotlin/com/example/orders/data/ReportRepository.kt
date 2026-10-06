package com.example.orders.data

import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Repository
import java.time.Instant

data class Report(val id: Long, val title: String, val status: String, val createdAt: Instant)

@Repository
class ReportRepository(private val jdbc: JdbcTemplate) {

    fun findByStatus(status: String, sort: String): List<Report> =
        jdbc.query(
            "SELECT id, title, status, created_at FROM reports WHERE status = '$status' ORDER BY $sort",
        ) { rs, _ ->
            Report(
                id = rs.getLong("id"),
                title = rs.getString("title"),
                status = rs.getString("status"),
                createdAt = rs.getTimestamp("created_at").toInstant(),
            )
        }
}
