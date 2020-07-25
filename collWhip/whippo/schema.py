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
from .snippets.serializers import UserSerializer
from django.contrib.auth import get_user_model


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class UserNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (relay.Node, )

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

        return CrawlDiscogPage('yup i run')

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    user = graphene.Field(UserNode)

    def mutate(self, info, username, password, first_name, last_name):
        validated = {"username": username, "password": password,
                     "first_name": first_name, "last_name": last_name}

        createdUser = UserSerializer().create(validated_data=validated)

        return CreateUser(user=createdUser)


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

        #hack get default have desc
        all_albums = all_albums.annotate(sorting_int=Cast('price', IntegerField())).order_by('-sorting_int', 'price').order_by('-have')

        if minHaveCount and maxHaveCount:
            inHaveRange = [album for album in all_albums if album.have >= minHaveCount and album.have <= maxHaveCount]
        elif minHaveCount:
            inHaveRange = [album for album in all_albums if album.have >= minHaveCount]
        elif maxHaveCount:
            inHaveRange = [album for album in all_albums if album.have <= maxHaveCount]

        resultAmountBeforePagination = len(inHaveRange)

        if skip:
            inHaveRange = inHaveRange[skip:]
        
        if first:
            inHaveRange = inHaveRange[:first]

        print('after inRange', len(inHaveRange))

        return { 'totalCount': resultAmountBeforePagination, 'edges': inHaveRange }



class Mutation(object):
    crawl_discog= CrawlDiscogPage.Field()

    create_user = CreateUser.Field(
    )

