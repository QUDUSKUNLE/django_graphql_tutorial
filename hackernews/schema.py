import graphene
import graphql_jwt
import links.schema
import users.schema
import links.schema_relay
import users.schema_relay


class Query(
    users.schema.Query,
    users.schema_relay.RelayQuery,

    links.schema.Query,
    links.schema_relay.RelayQuery,
    graphene.ObjectType
):
    pass

class Mutation(
    users.schema.Mutation,
    users.schema_relay.RelayMutation,

    links.schema.Mutation,
    links.schema_relay.RelayMutation,
    
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)



#-------------------Relay implementation----------------#
# class LinkNode(DjangoObjectType):
#     class Meta:
#         model = Link
#         filter_fields = ['id', 'url', 'description']
#         interfaces = (relay.Node, )

# class VoteNode(DjangoObjectType):
#     class Meta:
#         model = Vote
#         filter_fields = ['id']
#         interfaces = (relay.Node, )


# class Query(object):
#     link = relay.Node.Field(LinkNode)
#     all_links = DjangoFilterConnectionField(LinkNode)

#     vote = relay.Node.Field(VoteNode)
#     all_votes = DjangoFilterConnectionField(VoteNode)
    