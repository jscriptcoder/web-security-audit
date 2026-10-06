package com.example.orders.imports

import com.example.orders.data.Order
import com.example.orders.data.OrderRepository
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestParam
import org.springframework.web.bind.annotation.RestController
import org.springframework.web.multipart.MultipartFile
import java.io.ObjectInputStream
import java.io.Serializable
import java.math.BigDecimal

data class LegacyOrderLine(val customerId: String, val address: String, val total: BigDecimal) : Serializable

data class LegacyOrderBatch(val source: String, val lines: List<LegacyOrderLine>) : Serializable

data class ImportResult(val imported: Int, val details: List<String>)

@RestController
@RequestMapping("/api/imports")
class ImportController(
    private val orders: OrderRepository,
    private val catalog: XmlCatalogImporter,
) {

    @PostMapping("/legacy-orders")
    fun importLegacyOrders(@RequestParam("file") file: MultipartFile): ImportResult {
        val batch = ObjectInputStream(file.inputStream).use { it.readObject() as LegacyOrderBatch }
        val saved = batch.lines.map {
            orders.save(Order(customerId = it.customerId, shippingAddress = it.address, total = it.total))
        }
        return ImportResult(saved.size, listOf("source=${batch.source}"))
    }

    @PostMapping("/catalog")
    fun importCatalog(@RequestParam("file") file: MultipartFile): ImportResult {
        val names = catalog.productNames(file.inputStream)
        return ImportResult(names.size, names)
    }
}
