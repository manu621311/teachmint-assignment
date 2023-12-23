from rest_framework import serializers

class SplitSerializer(serializers.Serializer):
    userId = serializers.CharField()
    inSplit = serializers.BooleanField(default=True, help_text="Whether to include this person in split or not")
    percent = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, help_text="For percent split when calculating weightage", default = 0, max_value=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default = 0.00)
    hasPaid = serializers.BooleanField(default=False, help_text="Whether this person has paid or he ows")


class AcquaintanceSerializer(serializers.Serializer):
    userId = serializers.CharField()
    numberOfPeople = serializers.IntegerField(max_value=1000)


class ExpenseSerialzer(serializers.Serializer):
    CHOICES = ["EQUAL", "EXACT", "PERCENT"]

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    split = SplitSerializer(
        many=True, help_text="Users", required=True
    )
    acquaintance = AcquaintanceSerializer(
        many=True,
        required=False,
        help_text="Other people from family or friends of a user",
    )
    expenseType = serializers.ChoiceField(choices=CHOICES)
