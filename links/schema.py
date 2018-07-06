
"""
    In GraphQL, a Type is an object that may contain multiple fields.
    Each field is calculated through resolvers, that returns a value.
    A collection of types is called a schema. Every schema has a special type 
    called query for getting data from the server and mutation for
    sending data to the server


    The process of sending data to server is called mutation.
    Defining it is pretty similar on how you’ve defined the query.
"""

import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphene_django.filter import DjangoFilterConnectionField

from .models import Link, Vote
from users.schema import UserType


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None
        link = Link(
            url=url,
            description=description,
            posted_by=user)

        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('You must be logged to vote!')
        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link')

        Vote.objects.create(
            user=user,
            link=link,
        )
        return CreateVote(user=user, link=link)


class Query(graphene.ObjectType):
    links = graphene.List(
        LinkType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),)
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) | Q(description__icontains=search))
            
            qs = qs.filter(filter)
        if skip:
            qs = qs[skip::]
        
        if first:
            qs = qs[:first]

        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
