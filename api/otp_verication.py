from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(email=email)

            # Check if OTP is correct
            if user.otp != otp:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if OTP is expired (5-minute expiry)
            if now() > user.otp_created_at + timedelta(minutes=5):
                return Response({"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

          
            user.is_verified = True
            user.otp = None  
            user.save()

            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
