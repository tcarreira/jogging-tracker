from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
def hello_world(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class Logout(APIView):
    """Add logout capabilities to rest_framework.authtoken"""

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
