package com.example.orders.web

import com.example.orders.data.Report
import com.example.orders.data.ReportRepository
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController

@RestController
class ReportController(private val reports: ReportRepository) {

    @GetMapping("/api/reports")
    fun list(
        @RequestParam(defaultValue = "OPEN") status: String,
        @RequestParam(defaultValue = "created_at") sort: String,
    ): List<Report> = reports.findByStatus(status, sort)
}
