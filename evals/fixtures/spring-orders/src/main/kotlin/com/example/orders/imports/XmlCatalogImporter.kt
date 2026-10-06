package com.example.orders.imports

import org.springframework.stereotype.Component
import java.io.InputStream
import javax.xml.parsers.DocumentBuilderFactory

@Component
class XmlCatalogImporter {

    fun productNames(xml: InputStream): List<String> {
        val doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(xml)
        val nodes = doc.getElementsByTagName("name")
        return (0 until nodes.length).map { nodes.item(it).textContent.trim() }
    }
}
