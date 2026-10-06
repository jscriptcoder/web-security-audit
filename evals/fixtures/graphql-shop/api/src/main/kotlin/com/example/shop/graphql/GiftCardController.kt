package com.example.shop.graphql

import com.example.shop.data.CustomerRepository
import com.example.shop.data.GiftCardRepository
import org.springframework.graphql.data.method.annotation.Argument
import org.springframework.graphql.data.method.annotation.MutationMapping
import org.springframework.security.access.AccessDeniedException
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.annotation.AuthenticationPrincipal
import org.springframework.security.oauth2.jwt.Jwt
import org.springframework.stereotype.Controller
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

data class RedeemResult(val success: Boolean, val creditBalance: BigDecimal?, val message: String?)

@Controller
class GiftCardController(
    private val giftCards: GiftCardRepository,
    private val customers: CustomerRepository,
) {

    @MutationMapping
    @PreAuthorize("isAuthenticated()")
    @Transactional
    fun redeemGiftCard(@Argument code: String, @AuthenticationPrincipal jwt: Jwt): RedeemResult {
        val me = customers.findBySubject(jwt.subject) ?: throw AccessDeniedException("Unknown customer")
        val card = giftCards.findByCodeAndRedeemedFalse(code)
            ?: return RedeemResult(false, null, "Invalid or already redeemed code")
        card.redeemed = true
        me.creditBalance += card.amount
        return RedeemResult(true, me.creditBalance, null)
    }
}
