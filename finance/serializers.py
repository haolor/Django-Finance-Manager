from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Category, Transaction, Budget, SpendingPattern


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color', 'type', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'category', 'category_name', 'category_icon', 'category_color', 'category_type',
            'amount', 'description', 'transaction_date', 'original_nlp_input',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        # Validate that category type matches transaction type
        if 'category' in attrs and attrs['category']:
            category = attrs['category']
            # Note: We'll handle income/expense logic in views
        return attrs


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'amount', 'period',
            'start_date', 'end_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SpendingPatternSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SpendingPattern
        fields = [
            'id', 'category', 'category_name', 'average_amount',
            'frequency', 'last_transaction_date', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

