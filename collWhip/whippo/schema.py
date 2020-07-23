# collWhip/whippo/schema.py
import graphene
from graphene import relay, ObjectType, String, Mutation
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.core import management
from django.core.management.commands import loaddata
from django.db.models import IntegerField
from django.db.models.functions import Cast

from whippo.models import Album, Style

# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class AlbumNode(DjangoObjectType):
    class Meta:
        model = Album
        filter_fields = ['name', 'style']
        interfaces = (relay.Node, )

class StyleNode(DjangoObjectType):
    class Meta:
        model = Style
        interfaces = (relay.Node, )

class AlbumsCollection(graphene.ObjectType):
    class Meta:
        model = Album

    totalCount = graphene.Int(required=True)
    edges = graphene.List(AlbumNode)


class CrawlDiscogPage(graphene.Mutation):
    class Arguments:
        webpageURL = graphene.String(required=True)
    
    success = graphene.String()

    def mutate(self, info, webpageURL):
        print('run crawlDiscog')

        management.call_command('crawlDiscogsPage')

        return CrawlDiscogPage('yup i run')


class Query(object):
    album = relay.Node.Field(AlbumNode)
    albums = graphene.List(AlbumNode)

    albumsByHave = graphene.Field(
        AlbumsCollection,
        minHaveCount=graphene.Int(),
        maxHaveCount=graphene.Int(),
        first=graphene.Int(),
        skip=graphene.Int(),
        style=graphene.String(),
    )

    style = relay.Node.Field(StyleNode)
    styles = graphene.List(StyleNode)

    def resolve_albums(self, info, **kwargs):
        return Album.objects.all()

    def resolve_styles(self, info, **kwargs):
        return Style.objects.all()


    def resolve_albumsByHave(self, info, minHaveCount=1, maxHaveCount=None, first=None, skip=None, style=None, **kwargs):
        all_albums = Album.objects.all()

        if style:
            all_albums = all_albums.filter(style=style)

        all_albums = all_albums.order_by('have')

        all_albums = all_albums.annotate(sorting_int=Cast('price', IntegerField())).order_by('-sorting_int', 'price')

        if minHaveCount and maxHaveCount:
            inHaveRange = [album for album in all_albums if album.have >= minHaveCount and album.have <= maxHaveCount]
        elif minHaveCount:
            inHaveRange = [album for album in all_albums if album.have >= minHaveCount]
        elif maxHaveCount:
            inHaveRange = [album for album in all_albums if album.have <= maxHaveCount]

        # inHaveRange = sorted(inHaveRange, key=self.filterHave)
        # print('inRange', len(inHaveRange))

        # inHaveRange.sort(key=filterHave)
        resultAmountBeforePagination = len(inHaveRange)

        if skip:
            inHaveRange = inHaveRange[skip:]
        
        if first:
            inHaveRange = inHaveRange[:first]

        print('after inRange', len(inHaveRange))

        return { 'totalCount': resultAmountBeforePagination, 'edges': inHaveRange }



class Mutation(object):
    crawl_discog= CrawlDiscogPage.Field()