import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, User, ChatRoomParticipant
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy user từ scope (đã được thêm bởi middleware)
        self.user = self.scope['user']
        
        # Khởi tạo room_name và room_group_name
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Debug để xác định các giá trị
        print(f"DEBUG: User: {self.user}, Room Name: {self.room_name}")

        # Kiểm tra người dùng đã đăng nhập
        if not self.user or hasattr(self.user, 'is_anonymous') and self.user.is_anonymous:
            print("⚠️ WebSocket connection denied: Anonymous user")
            await self.close(code=4003)
            return

        # Xử lý ID phòng chat từ URL
        # Lấy chatroom_id từ room_name, xử lý cả 2 dạng "chat_XXX" và "chat-XXX"
        if self.room_name.startswith('chat_'):
            chatroom_id = self.room_name.replace('chat_', 'chat-')
        elif self.room_name.startswith('chat-'):
            chatroom_id = self.room_name
        else:
            chatroom_id = f'chat-{self.room_name}'
        
        print(f"DEBUG: Looking for chatroom_id: {chatroom_id}")
        
        try:
            # Lấy thông tin phòng chat
            chatroom = await self.get_chatroom(chatroom_id)
            if not chatroom:
                print(f"⚠️ WebSocket connection denied: Chatroom {chatroom_id} not found")
                await self.close(code=4004)
                return
                
            # Kiểm tra người dùng có phải là thành viên của phòng hoặc là admin
            is_member = await self.is_user_in_chatroom(self.user.user_id, chatroom_id)
            is_admin = getattr(self.user, 'role', '') == 'Admin'
            
            print(f"DEBUG: User {self.user.user_id} is_member: {is_member}, is_admin: {is_admin}")
            
            if not is_member and not is_admin:
                print(f"⚠️ WebSocket connection denied: User {self.user.user_id} not in chatroom {chatroom_id}")
                await self.close(code=4003)
                return
                
            # Tham gia vào nhóm WebSocket
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Chấp nhận kết nối WebSocket
            await self.accept()
            
            print(f"✅ WebSocket connection accepted for user: {self.user.user_id} to room: {chatroom_id}")
            
            # Gửi tin nhắn chào mừng hoặc thông báo trạng thái - SỬA LỖI Ở ĐÂY
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': f'Connected to chat room {chatroom_id}'
            }))
            
        except Exception as e:
            print(f"⚠️ Error in connect: {str(e)}")
            await self.close(code=4500)

    @database_sync_to_async
    def get_chatroom(self, chatroom_id):
        try:
            return ChatRoom.objects.get(chatroom_id=chatroom_id)
        except ChatRoom.DoesNotExist:
            return None
            
    @database_sync_to_async
    def is_user_in_chatroom(self, user_id, chatroom_id):
        # Kiểm tra xem người dùng có phải là thành viên của phòng chat hay không
        return ChatRoomParticipant.objects.filter(
            user_id=user_id,
            chatroom_id=chatroom_id
        ).exists()
        
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'mark_read':
                await self.handle_mark_read(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            # WebRTC signaling message handling
            elif message_type == 'call_offer':
                await self.handle_call_offer(data)
            elif message_type == 'call_answer':
                await self.handle_call_answer(data)
            elif message_type == 'ice_candidate':
                await self.handle_ice_candidate(data)
            elif message_type == 'call_end':
                await self.handle_call_end(data)
        except json.JSONDecodeError:
            pass
    
    async def handle_chat_message(self, data):
        # Process and save the message
        message = await self.save_message(data)
        
        # Log for debugging with more information
        print(f"📨 Message saved and broadcasting: {message['message_id']}, content: {message['content']}, to room: {self.room_group_name}, sender: {message['sent_by']}")
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    async def handle_mark_read(self, data):
        # Mark messages as read
        await self.mark_messages_read(data)
        
        # Send update to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'messages_read',
                'message_ids': data.get('message_ids', []),
                'user_id': data.get('user_id')
            }
        )
    
    async def handle_typing_indicator(self, data):
        # Send typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': data.get('user_id'),
                'username': data.get('username', 'User'),
                'is_typing': data.get('is_typing', False)
            }
        )

    # WebRTC Signaling Handlers
    async def handle_call_offer(self, data):
        print(f"📞 Received call offer from {data.get('userId')} for room {data.get('roomId')}")
        
        # For group calls, we need to know who the target is
        target_participant_id = data.get('targetParticipantId')
        
        if target_participant_id:
            print(f"📞 Call offer is for specific participant: {target_participant_id}")
            # Forward the offer only to the specific participant
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_offer',
                    'data': data,
                    'target_participant_id': target_participant_id
                }
            )
        else:
            # For backward compatibility with one-on-one calls
            print(f"📞 Broadcasting call offer to all participants in room")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_offer',
                    'data': data
                }
            )

    async def handle_call_answer(self, data):
        print(f"📞 Received call answer from {data.get('userId')} for room {data.get('roomId')}")
        
        # For group calls, we need to know who the target is
        target_participant_id = data.get('targetParticipantId')
        
        if target_participant_id:
            print(f"📞 Call answer is for specific participant: {target_participant_id}")
            # Forward the answer only to the specific participant
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_answer',
                    'data': data,
                    'target_participant_id': target_participant_id
                }
            )
        else:
            # For backward compatibility with one-on-one calls
            print(f"📞 Broadcasting call answer to all participants in room")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_answer',
                    'data': data
                }
            )

    async def handle_ice_candidate(self, data):
        print(f"🧊 Received ICE candidate from {data.get('userId')} for room {data.get('roomId')}")
        
        # For group calls, we need to know who the target is
        target_participant_id = data.get('targetParticipantId')
        
        if target_participant_id:
            print(f"🧊 ICE candidate is for specific participant: {target_participant_id}")
            # Forward the ICE candidate only to the specific participant
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_ice_candidate',
                    'data': data,
                    'target_participant_id': target_participant_id
                }
            )
        else:
            # For backward compatibility with one-on-one calls
            print(f"🧊 Broadcasting ICE candidate to all participants in room")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_ice_candidate',
                    'data': data
                }
            )

    async def handle_call_end(self, data):
        print(f"📞 Received call end from {data.get('userId')} for room {data.get('roomId')}")
        
        # Broadcast call end to all participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_call_end',
                'data': data
            }
        )

    # WebRTC Message Dispatchers
    async def webrtc_offer(self, event):
        data = event['data']
        target_participant_id = event.get('target_participant_id')
        
        # Check if this message is for a specific participant
        if target_participant_id and str(self.user.user_id) != str(target_participant_id):
            print(f"Skip forwarding offer - targeted participant {target_participant_id} doesn't match {self.user.user_id}")
            return
        
        # Send the offer to the client
        print(f"Sending call offer to user {self.user.user_id}")
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'signal_type': 'call_offer',
            'sdp': data.get('sdp'),
            'userId': data.get('userId'),
            'isAudioOnly': data.get('isAudioOnly', False)
        }))

    async def webrtc_answer(self, event):
        data = event['data']
        target_participant_id = event.get('target_participant_id')
        
        # Check if this message is for a specific participant
        if target_participant_id and str(self.user.user_id) != str(target_participant_id):
            print(f"Skip forwarding answer - targeted participant {target_participant_id} doesn't match {self.user.user_id}")
            return
            
        # Send the answer to the client
        print(f"Sending call answer to user {self.user.user_id}")
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'signal_type': 'call_answer',
            'sdp': data.get('sdp'),
            'userId': data.get('userId')
        }))

    async def webrtc_ice_candidate(self, event):
        data = event['data']
        target_participant_id = event.get('target_participant_id')
        
        # Check if this message is for a specific participant
        if target_participant_id and str(self.user.user_id) != str(target_participant_id):
            print(f"Skip forwarding ICE candidate - targeted participant {target_participant_id} doesn't match {self.user.user_id}")
            return
            
        # Send the ICE candidate to the client
        print(f"Sending ICE candidate to user {self.user.user_id}")
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'signal_type': 'ice_candidate',
            'candidate': data.get('candidate'),
            'userId': data.get('userId')
        }))

    async def webrtc_call_end(self, event):
        data = event['data']
        
        # Send the call end to all clients
        print(f"Sending call end to user {self.user.user_id}")
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signal',
            'signal_type': 'call_end',
            'userId': data.get('userId')
        }))
    
    async def chat_message(self, event):
        print(f"🔔 Sending chat message to client: {event['message'].get('message_id', 'unknown')}")
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def messages_read(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'message_ids': event['message_ids'],
            'user_id': event['user_id']
        }))
    
    async def typing_indicator(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def is_participant(self, chatroom_id, user_id):
        try:
            chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
            return chatroom.participants.filter(user_id=user_id).exists()
        except ChatRoom.DoesNotExist:
            return False
            
    @database_sync_to_async
    def save_message(self, data):
        # Create a new message
        import uuid
        message_id = f"msg-{str(uuid.uuid4())[:8]}"
        
        # Xử lý chatroom_id từ nhiều nguồn khác nhau
        chatroom_id = data.get('chatroom_id') or data.get('chatroom') or self.room_name
        
        # Nếu chatroom_id bắt đầu bằng 'chat_', chuyển thành 'chat-'
        if chatroom_id and chatroom_id.startswith('chat_'):
            chatroom_id = chatroom_id.replace('chat_', 'chat-')
        elif chatroom_id and not (chatroom_id.startswith('chat_') or chatroom_id.startswith('chat-')):
            chatroom_id = f"chat-{chatroom_id}"
        
        print(f"DEBUG: Saving message to chatroom_id: {chatroom_id}")
        chatroom = ChatRoom.objects.get(chatroom_id=chatroom_id)
        
        # Lấy sender_id từ data hoặc sử dụng người dùng hiện tại
        sender_id = data.get('sender_id') or self.user.user_id
        sender = User.objects.get(user_id=sender_id)
        
        receiver = None
        if data.get('receiver_id'):
            try:
                receiver = User.objects.get(user_id=data.get('receiver_id'))
            except User.DoesNotExist:
                pass
        
        message = Message.objects.create(
            message_id=message_id,
            content=data.get('content'),
            chatroom=chatroom,
            sent_by=sender,
            receiver=receiver
        )
        
        # Manually serialize the message
        from api.serializers.message_serializer import MessageSerializer
        serializer = MessageSerializer(message)
        return serializer.data
    
    @database_sync_to_async
    def mark_messages_read(self, data):
        message_ids = data.get('message_ids', [])
        if message_ids:
            Message.objects.filter(message_id__in=message_ids).update(is_read=True)