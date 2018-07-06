import graphene
import django_filters
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Link, Vote


class LinkFilter(django_filters.FilterSet):
    class Meta:
        model = Link
        fields = ['url', 'description']


class VoteFilter(django_filters.FilterSet):
    class Meta:
        model = Vote
        fields = ['id']


class LinkNode(DjangoObjectType):
    class Meta:
        model = Link
        interfaces = (relay.Node, )


class VoteNode(DjangoObjectType):
    class Meta:
        model = Vote
        interfaces = (relay.Node, )


class RelayQuery(graphene.ObjectType):
    relay_vote = graphene.relay.Node.Field(VoteNode)
    relay_votes = DjangoFilterConnectionField(
        VoteNode, filterset_class=VoteFilter)

    relay_link = graphene.relay.Node.Field(LinkNode)
    relay_links = DjangoFilterConnectionField(
        LinkNode, filterset_class=LinkFilter)


class RelayCreateLink(graphene.relay.ClientIDMutation):
    link = graphene.Field(LinkNode)

    class Input:
        url = graphene.String()
        description = graphene.String()

    def mutate_and_get_payload(root, info, **input):
        user = info.context.user or None

        link = Link(
            url=input.get('url'),
            description=input.get('description'),
            posted_by=user,
        )
        link.save()

        return RelayCreateLink(link=link)


class RelayCreateVote(graphene.relay.ClientIDMutation):
    vote = graphene.Field(VoteNode)

    class Input:
        link_id = graphene.Int()

    def mutate_and_get_payload(root, info, **input):
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

        return RelayCreateVote(user=user, link=link)


class RelayMutation(graphene.ObjectType):
    relay_create_link = RelayCreateLink.Field()
    relay_create_vote = RelayCreateVote.Field()
