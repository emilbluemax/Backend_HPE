from rest_framework import serializers

from .models import Product,User,Test

# model = db table
# Converting complex data - model instances and querysets into native python datatypes - rendered into json and xml - easily transmitted over a network
# ProductSerializer is a sub class of ModelSerializer
# model - db table is Product and all the fields inside the Prouct table must be serialized
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'