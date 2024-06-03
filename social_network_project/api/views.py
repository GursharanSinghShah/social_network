from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSignupSerializer, UserLoginSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from .models import FriendRequest
from .serializers import FriendRequestSerializer
from rest_framework.decorators import action

class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email__iexact=serializer.validated_data['email'])

        if not user.check_password(serializer.validated_data['password']):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSignupSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', '')
        return User.objects.filter(
            Q(email__iexact=keyword) | Q(username__icontains=keyword)
        )




class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def create(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = request.data.get('to_user')
        to_user = User.objects.get(id=to_user_id)
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user, status='pending')
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_requests(self, request):
        pending_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        return Response(FriendRequestSerializer(pending_requests, many=True).data)

    @action(detail=False, methods=['get'], url_path='friends')
    def friends(self, request):
        friends = FriendRequest.objects.filter(
            Q(from_user=request.user, status='accepted') |
            Q(to_user=request.user, status='accepted')
        )
        friends_users = [req.from_user if req.to_user == request.user else req.to_user for req in friends]
        return Response(UserSignupSerializer(friends_users, many=True).data)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept_request(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({"error": "You cannot accept this friend request"}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.status = 'accepted'
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_request(self, request, pk=None):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({"error": "You cannot reject this friend request"}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.status = 'rejected'
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data)
