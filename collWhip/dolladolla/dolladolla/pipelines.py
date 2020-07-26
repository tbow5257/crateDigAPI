# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from whippo.models import Album, Style

class DolladollaPipeline:
    def process_item(self, item, spider):

        if self.check_object_exists(item['releaseId']):
            return item

        if not self.check_related_field_exists(item['style']):
            newStyle = Style(name=item['style'])
            newStyle.save()

        album = Album(name=item['name'], 
                      releaseId=item['releaseId'], 
                      have=int(item['have']), 
                      want=int(item['want']),
                      price=int(item['price']),
                      style=item['style'])
        print('album ', album)
        album.save()

        return item

    def check_object_exists(self, uniqueValue):
        try:
           if Album.objects.get(releaseId=uniqueValue):
               return True
        except Album.DoesNotExist:
            return False

    def check_related_field_exists(self, relatedField):
        try:
           if Style.objects.get(name=relatedField):
               return True
        except Style.DoesNotExist:
            return False


