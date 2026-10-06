import { gql } from '@apollo/client';

export const PRODUCT_PAGE = gql`
  query ProductPage($id: ID!) {
    product(id: $id) {
      id
      name
      price
      reviews {
        id
        rating
        body
        author {
          id
          displayName
        }
      }
    }
  }
`;

export const MY_ACCOUNT = gql`
  query MyAccount {
    me {
      id
      displayName
      email
      phone
      creditBalance
      orders {
        id
        total
        status
        shippingAddress
      }
    }
  }
`;

export const REDEEM_GIFT_CARD = gql`
  mutation RedeemGiftCard($code: String!) {
    redeemGiftCard(code: $code) {
      success
      creditBalance
      message
    }
  }
`;
