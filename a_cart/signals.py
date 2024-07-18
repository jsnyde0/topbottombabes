from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from django.db import transaction
from .models import Cart
import logging

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def transfer_cart_to_authenticated_user(sender, request, user, **kwargs):
    """
    Transfer or merge the cart when a user logs in.

    This function is triggered when a user logs in. It handles various scenarios to ensure
    that the user's cart is properly maintained across sessions.
    """
    session_cart_id = request.session.get('cart_id')
    
    with transaction.atomic():
        # First, try to get an existing cart for the user
        user_cart, user_cart_created = Cart.objects.get_or_create(user=user)

        if session_cart_id:
            try:
                session_cart = Cart.objects.get(id=session_cart_id)
                if session_cart.user is None:
                    # If session cart exists but isn't associated with a user,
                    # merge it into the user's cart and delete the session cart
                    user_cart.merge_with(session_cart)
                    session_cart.delete()
                    logger.info(f"Merged anonymous cart {session_cart_id} into user's cart {user_cart.id}")
                elif session_cart.user != user:
                    # If session cart belongs to a different user (shouldn't normally happen),
                    # just use the current user's cart
                    logger.warning(f"Session cart {session_cart_id} belonged to a different user. Using {user}'s own cart.")
            except Cart.DoesNotExist:
                logger.warning(f"Cart with id {session_cart_id} not found")

    # Always update the session with the user's cart ID
    request.session['cart_id'] = user_cart.id
    request.session.modified = True
    logger.info(f"Using cart {user_cart.id} for user {user}")