from django.http import Http404

class Repository:    
    def __init__(self, model):
        self.model = model

    def create(self, validated_data):
        return self.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def create2(self, **kwargs):
        instance = self.model(**kwargs)
        instance.save()
        return instance

    def update2(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def update3(self, instance, **kwargs):
        for field, value in kwargs.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        instance.save()
        return instance
    
    def filter_objects(self, **filters):
        return self.model.objects.filter(**filters)
    
    def filters(self, *args, **kwargs):
        return self.model.objects.filter(*args, **kwargs)
    
    def get_all_objects(self):
        return self.model.objects.all()

    def get_object(self, **kwargs):
        try:
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            raise Http404

    
    def get_object_or_fail(self, **filters):
        try:
            return  self.model.objects.get(**filters)
        except self.model.DoesNotExist:
            return None

    def get_object_or_none(self, model, **filters):
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            return None
