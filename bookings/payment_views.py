import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    """Create a Stripe payment intent for a booking."""
    
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            
            # Calculate amount in cents
            amount_cents = int(booking.balance_due * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata={
                    'booking_id': booking.id,
                    'booking_number': booking.booking_number,
                }
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'amount': booking.balance_due,
                'currency': 'usd'
            })
            
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeWebhookView(APIView):
    """Handle Stripe webhook events."""
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self._handle_payment_success(payment_intent)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self._handle_payment_failure(payment_intent)
        
        return Response({'status': 'success'})
    
    def _handle_payment_success(self, payment_intent):
        """Handle successful payment."""
        booking_id = payment_intent['metadata']['booking_id']
        amount = payment_intent['amount'] / 100  # Convert from cents
        
        try:
            booking = Booking.objects.get(id=booking_id)
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_method=Payment.METHOD_CREDIT_CARD,
                transaction_id=payment_intent['id'],
                status=Payment.STATUS_COMPLETED
            )
            
            # Update booking payment status
            booking.record_payment(amount)
            
        except Booking.DoesNotExist:
            pass  # Log error in production
    
    def _handle_payment_failure(self, payment_intent):
        """Handle failed payment."""
        booking_id = payment_intent['metadata']['booking_id']
        
        try:
            booking = Booking.objects.get(id=booking_id)
            
            # Create failed payment record
            Payment.objects.create(
                booking=booking,
                amount=payment_intent['amount'] / 100,
                payment_method=Payment.METHOD_CREDIT_CARD,
                transaction_id=payment_intent['id'],
                status=Payment.STATUS_FAILED
            )
            
        except Booking.DoesNotExist:
            pass  # Log error in production
