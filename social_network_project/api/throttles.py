from rest_framework.throttling import SimpleRateThrottle

class FriendRequestThrottle(SimpleRateThrottle):
    scope = 'friend_request'

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None
        return f'{self.scope}_{request.user.id}'