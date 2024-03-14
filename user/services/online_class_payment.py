import stripe
from django.conf import settings
from django.http import Http404
from repositories.repository import Repository
from classes.models import OnlineClass, ClassEnrollment
from django.utils import timezone
from rest_framework import status

stripe.api_key = settings.STRIPE_API_KEY

class OnlineClassPaymentService:
    def __init__(self):
        self.online_class_repository = Repository(OnlineClass)
        self.enrollment_repository = Repository(ClassEnrollment)

    def process_payment(self, user, class_id, token):
        online_class = self.online_class_repository.get_object_or_fail(id=class_id)
        if not online_class:
            raise Http404("Class not found")
        
        if online_class.is_active == False:
            raise Http404("Class deactivated. Contact Admin")
        
        existing_enrollment = self.enrollment_repository.filter_objects(
            user=user, 
            online_class_id=class_id, 
            paid=True
        )
        
        if existing_enrollment.exists():
            # If user has already paid for the class
            return {"message": "You have already paid for this class."}, status.HTTP_409_CONFLICT

        
        # Convert class price to the amount in cents for Stripe
        amount = int(online_class.price * 100)

        # Attempt to create a charge using Stripe
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                description=f'Payment for class {online_class.title}',
                source=token,
            )

            # If the charge is successful, record the enrollment and payment
            self.enrollment_repository.create({
                'user': user,
                'online_class': online_class,
                'paid': True,
                'payment_date': timezone.now(),
                'amount_paid': online_class.price
            })
            
            return {"message": "Payment successful", "charge": charge.id}, status.HTTP_200_OK

        except stripe.error.CardError as e:
            # The card has been declined or there are insufficient funds
            err = e.json_body.get('error', {})
            return {"message": "Payment failed", "error": err.get('message')}, status.HTTP_400_BAD_REQUEST

        except stripe.error.StripeError as e:
            # General Stripe error (networking issues, Stripe's downtime, etc)
            print(f"Stripe error: {e}")
            return {"message": "Payment processing failed. Please try again later."}, status.HTTP_400_BAD_REQUEST

        except Exception as e:
            # Other exceptions
            print(f"Unexpected error: {e}")
            return {"message": "An unexpected error occurred."}, status.HTTP_400_BAD_REQUEST