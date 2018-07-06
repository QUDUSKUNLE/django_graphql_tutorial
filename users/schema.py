import graphene

from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


####-----------------Query------------------------------##########
class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    users = graphene.List(UserType)

    def resolve_users(self, info):
        user = info.context.user
        if not user.is_superuser:
            raise Exception('Not authorized to view this')
    
        return get_user_model().objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return Exception('Authentication credentials were not provided')

        return user


######--------------------- Mutations----------------------############
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)


    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
