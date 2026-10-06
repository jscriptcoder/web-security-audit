package com.example.shop.giftcards

import com.example.shop.data.GiftCard
import com.example.shop.data.GiftCardRepository
import org.springframework.stereotype.Service
import java.math.BigDecimal
import java.security.SecureRandom

@Service
class GiftCardIssuer(private val giftCards: GiftCardRepository) {
    private val random = SecureRandom()

    /** Codes are printed on physical cards sold in stores, so they are kept short enough to type. */
    fun issue(amount: BigDecimal): GiftCard =
        giftCards.save(GiftCard(code = "%06d".format(random.nextInt(1_000_000)), amount = amount))
}
