from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, User , Test# The 2 table - model creaeted - model classes
from .producer import publish
from .serializers import ProductSerializer,UserSerializer,TestSerializer
import random

# subclasses
class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_created', serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def update(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)# The data is being updated hence the new data is sent over the request
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_updated', serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None): # Pass the ID of the product to be deleted from the URL
        product = Product.objects.get(id=pk) # Fetching the record - given ID
        product.delete()
        publish('product_deleted', pk) # Publishing onto the RabbitMQ queue
        return Response(status=status.HTTP_204_NO_CONTENT)


'''class UserAPIView(APIView):
    def get(self, _):
        users = User.objects.all()
        user = random.choice(users)
        return Response({
            'id': user.id
        })'''

'''class UserAPIView(APIView):
    def get(self,request, pk=None):
        #users = User.objects.get(id=pk)
        users = User.objects.all()
        #serializer = UserSerializer(users)
        serializer = UserSerializer(users, many=True)
        #user = random.choice(users)
        return Response(serializer.data)'''

class UserAPIView(APIView):
    def get(self,request, pk=None):
        users = User.objects.get(id=pk)
        #users = User.objects.all()
        serializer = UserSerializer(users)
        #serializer = UserSerializer(users, many=True)
        #user = random.choice(users)
        return Response(serializer.data)
    
class TestAPIView(APIView):
    def get(self, request):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)