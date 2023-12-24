from rest_framework import serializers


class SplitSerializer(serializers.Serializer):
    '''Class to input data of users involved in a split'''
    userId = serializers.CharField()
    percent = serializers.DecimalField(     #If method chosen is PERCENT, use this
        max_digits=5,
        decimal_places=2,
        required=False,
        help_text="For percent split when calculating weightage",
        default=0,
        max_value=100,
    )
    amount = serializers.DecimalField(      #If method chosen is 'not' PERCENT, use this
        max_digits=10, decimal_places=2, required=False, default=0.00
    )


class AcquaintanceSerializer(serializers.Serializer):
    '''Serialzer for an inputing friends of a user'''
    userId = serializers.CharField()
    numberOfPeople = serializers.IntegerField(max_value=1000)


class ExpenseSerialzer(serializers.Serializer):
    '''Serialzer for an expense'''
    CHOICES = ["EQUAL", "EXACT", "PERCENT"]
    payer = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True, max_length=20)
    note = serializers.CharField(required=False, allow_blank=True, max_length=50)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    split = SplitSerializer(many=True, help_text="Users", required=True)    #Users involved in split
    acquaintance = AcquaintanceSerializer(      #If any user has friends accompanying him
        many=True,
        required=False,
        help_text="Other people from family or friends of a user",
    )
    expenseType = serializers.ChoiceField(choices=CHOICES)


class SimplifySplitSerializer(serializers.Serializer):
    '''Serialzer which gets user ids for simplification'''
    userIds = serializers.ListField()
