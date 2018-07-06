import graphene
import django_filters

from graphene import relay
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType

from graphene_django.filter import DjangoFilterConnectionField


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username']


class UserNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (relay.Node, )


class RelayQuery(graphene.ObjectType):
    relay_user = graphene.relay.Node.Field(UserNode)
    relay_users = DjangoFilterConnectionField(
        UserNode, filterset_class=UserFilter)


class RelayCreateUser(graphene.relay.ClientIDMutation):
    user = graphene.Field(UserNode)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
    
    def mutate_and_get_payload(root, info, **input):
        user = get_user_model()(
            username=input.get('username'),
            email=input.get('email'),
        )

        user.set_password(password=input.get('password'))
        user.save()

        return RelayCreateUser(user=user)


class RelayMutation(graphene.ObjectType):
    relay_create_user = RelayCreateUser.Field()
