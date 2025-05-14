from api.models import Movie
from rest_framework import serializers

class MovieSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    release_date = serializers.DateField()
    rating = serializers.FloatField()

    def create(self, validated_data):
        return Movie.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.release_date = validated_data.get('release_date', instance.release_date)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance
    