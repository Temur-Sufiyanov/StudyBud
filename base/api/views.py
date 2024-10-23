from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializers

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET/api',
        'GET/api/rooms',
        'GET/api/rooms/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializers = RoomSerializers(rooms, many=True)
    
    return Response(serializers.data)

@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializers = RoomSerializers(room, many=False)
    
    return Response(serializers.data)