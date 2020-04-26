from rest_framework import serializers

from api_v0.models import User


class UserSerializer(serializers.ModelSerializer):

    user_id = serializers.CharField(max_length=200)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField(max_length=70)
    phone_number = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ("user_id", "first_name", "last_name", "full_name","email","phone_number")

class TaskSerializer(serializers.ModelSerializer):

    id = serializers.CharField(max_length=200)
    assigned_to_id = serializers.CharField(max_length=100)
    task_name = serializers.CharField(max_length=100)
    task_description = serializers.CharField(max_length=200)
    task_start_time = serializers.DateField()
    expected_completetion_time = serializers.DateField()
    actual_completetion_time = serializers.DateField()
    assigned_to = serializers.SerializerMethodField('_assigned_to')

    def _assigned_to(self, obj):
        try:
            user_obj = User.objects.get(user_id=obj['assigned_to_id'])
            return user_obj.full_name
        except:
            return None

    class Meta:
        model = User
        fields = ("id", "task_name", "assigned_to_id", "assigned_to", "task_description","task_start_time",
                  "expected_completetion_time","actual_completetion_time")
